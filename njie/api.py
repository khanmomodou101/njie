import frappe
from frappe.model.document import Document
import requests
from frappe.utils import getdate, flt
import random

def autoname(doc, method=None):
    doc.name = doc.phone_number

@frappe.whitelist()
def update_daily_expenses_in_sales_invoice(doc, method=None):
    total_expenses = 0
    total_cash_balance = 0
    for payment in doc.payments:
        if payment.mode_of_payment == "Cash":
            total_cash_balance += payment.amount

    for item in doc.items:
        total_expenses += item.custom_expenses
    doc.custom_total_expenses = total_expenses
    doc.custom_balance = total_cash_balance - total_expenses
# create daily report
@frappe.whitelist()
def create_daily_report():
    deposits = 0
    credit = 0
    withdrawals = 0
    credit_payments = 0
    transactions = frappe.get_list(
        "Transactions",
        fields=["transaction_type", "amount"],
        filters={"date": frappe.utils.today()},
    )
    for transaction in transactions:
        if transaction.transaction_type == "Deposit":
            deposits += transaction.amount
        elif transaction.transaction_type == "Credit":
            credit += transaction.amount
        elif transaction.transaction_type == "Withdrawal":
            withdrawals += transaction.amount
        elif transaction.transaction_type == "Credit Payment":
            credit_payments += transaction.amount

    # create a new daily report
    daily_report = frappe.new_doc("Daily Report")
    daily_report.date = frappe.utils.today()
    daily_report.deposits = deposits
    daily_report.credit = credit
    daily_report.withdrawals = withdrawals
    daily_report.credit_payments = credit_payments
    daily_report.save()
    frappe.db.commit()

  


@frappe.whitelist()
def get_data():
    transactions = frappe.get_list(
        "Transactions",
        fields=["customer_name", "date", "transaction_type", "amount"],
    )
    data = []
    for transaction in transactions:
        data.append(transaction.customer_name)
        data.append(transaction.date)
        data.append(transaction.transaction_type)
        data.append(transaction.amount)
    return data
@frappe.whitelist()
def update_customer():
    # update customer branch to Njie Charakh World Market 1
    frappe.db.sql(
        "UPDATE `tabTransactions` SET branch = 'Njie Charakh World Market 1'")
    frappe.db.commit()

@frappe.whitelist()
def get_date():
    # return the current year 
    from frappe.utils import today, getdate
    year = "2023"
    first_day = getdate(year + "-01-01")
    last_day = getdate(year + "-12-31")
    return first_day
    
    

@frappe.whitelist()
def get_blogs():
    try:
        blogs  = frappe.get_list("Blog Post", fields=["title", "published_on", "blog_intro", "content", "blog_category"])
        frappe.local.response.update({
            "http_status_code": 200,
            "data": blogs
        })
    except Exception as e:
        frappe.local.response.update({
            "http_status_code": 500,
            "error": str(e)
        })

# id: 'household-001',
#         name: 'Premium Cookware Set',
#         description: 'High-quality cooking utensils for your kitchen',
#         category: 'Household Items',
#         price: 'From D3,500',
#         image: 'https://images.unsplash.com/photo-1590794056226-187342175e2f?q=80&w=800&auto=format',
#         features: ['Durable materials', 'Complete set', 'Non-stick coating']
@frappe.whitelist(allow_guest=True)
def get_products():
    try:
        products = frappe.get_list("Website Item")
        data = []
        for product in products:
            doc = frappe.get_doc("Website Item", product.name)
            price = frappe.db.get_value("Item Price", {"item_code": product.web_item_name}, "price_list_rate")
            data.append({
                "id": doc.web_item_name,
                "name": doc.web_item_name,
                "category": doc.item_group,
                "image": frappe.utils.get_url(doc.thumbnail) if doc.thumbnail else "https://njie.royalsmb.com/files/njie_harakha_logo_-removebg-preview.png",
                "description": doc.short_description,
                "price": f"From D{price}" if price else "From D0",
                "features": doc.website_specifications
            })
        frappe.local.response.update({
            "http_status_code": 200,
            "data": data
        })
    except Exception as e:
        frappe.local.response.update({
            "http_status_code": 500,
            "error": str(e)
        })

@frappe.whitelist()
def update_transactions(doctype):
    docs = frappe.get_all(doctype)
    for doc in docs:
        doc_transaction = frappe.get_doc(doctype, doc.name)
        customer = frappe.get_doc('Customer', doc_transaction.customer)
        frappe.get_doc({
			'doctype': 'Transactions',
			'date': doc_transaction.posting_date,
			'transaction_type': doctype,
			'amount': doc_transaction.amount,
			'customer_name': doc_transaction.customer_name,
			"branch": customer.custom_branch,
			"batch": customer.custom_batch
		}).insert()
    frappe.db.commit()
    return "Success"

@frappe.whitelist()
def update_trans(doctype):
    # Fetch all transactions in one query
    transactions = frappe.db.sql(f"""
        SELECT name, posting_date, customer, customer_name, total_amount
        FROM `tab{doctype}`
    """, as_dict=True)

    if not transactions:
        return "No transactions found"

    
    for t in transactions:
        customer_info = frappe.get_doc("Customer", t["customer"])
        frappe.get_doc({
            "doctype": "Transactions",
            "date": t["posting_date"],
            "transaction_type": doctype,
            "amount": t["total_amount"],
            "customer_name": t["customer_name"],
            "branch": customer_info.get("custom_branch"),
            "batch": customer_info.get("custom_batch")
        }).insert()
    frappe.db.commit()

    
    return "Success"

@frappe.whitelist()
def delete_transactions():
    frappe.db.sql("DELETE FROM `tabTransactions`")
    frappe.db.commit()
    return "Success"



@frappe.whitelist()
def auto_generate_barcode():
    items = frappe.get_all("Item", fields=["name"])

    for item in items:
        doc = frappe.get_doc("Item", item.name)

        # Skip if item already has at least one barcode
        if doc.barcodes:
            continue

        barcode = None
        while True:
            # Generate a random 10-digit number with leading zeros
            candidate = str(random.randint(0, 10**10 - 1)).zfill(10)

            # Check if barcode exists in Item Barcode child table
            exists = frappe.db.exists("Item Barcode", {"barcode": candidate})
            if not exists:
                barcode = candidate
                break  # Found a unique barcode

        # Append to child table
        doc.append("barcodes", {
            "barcode": barcode
        })

        # Save the item
        doc.flags.ignore_mandatory = True
        doc.save()

    frappe.db.commit()
    return "Unique barcodes generated for items without barcodes."

@frappe.whitelist()
def generate_barcode_after_save(doc, method=None):

    if doc.is_stock_item and not doc.barcodes:
        
        barcode = None
        while True:
            candidate = str(random.randint(0, 10**10 - 1)).zfill(10)

            # Check if barcode exists in Item Barcode child table
            exists = frappe.db.exists("Item Barcode", {"barcode": candidate})
            if not exists:
                barcode = candidate
                break  # Found a unique barcode

        # Append to child table
        doc.append("barcodes", {
            "barcode": barcode
        })

        # Save the item
        doc.flags.ignore_mandatory = True
        doc.save()

        frappe.db.commit()
