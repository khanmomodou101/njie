import frappe
from frappe.model.document import Document
import requests
from frappe.utils import getdate, flt
import random
from datetime import datetime, timedelta
import os
import tempfile
import base64
from io import BytesIO

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



def generate_valid_ean13():
    """Generate a valid EAN-13 barcode with proper check digit"""
    # Generate 12 random digits
    digits = [random.randint(0, 9) for _ in range(12)]
    
    # Calculate check digit using EAN-13 algorithm
    odd_sum = sum(digits[i] for i in range(0, 12, 2))  # positions 1, 3, 5, 7, 9, 11
    even_sum = sum(digits[i] for i in range(1, 12, 2))  # positions 2, 4, 6, 8, 10, 12
    
    total = odd_sum + (even_sum * 3)
    check_digit = (10 - (total % 10)) % 10
    
    # Add check digit to complete the EAN-13
    digits.append(check_digit)
    
    return ''.join(map(str, digits))

@frappe.whitelist()
def auto_generate_barcode():
    items = frappe.get_all("Item", fields=["name"])

    for item in items:
        doc = frappe.get_doc("Item", item.name)

        # Skip if item already has at least one barcode
        # if doc.barcodes:
        #     continue
        doc.barcodes = []

        barcode_number = None
        while True:
            # Generate a valid EAN-13 number
            candidate = generate_valid_ean13()

            # Check if barcode exists in Item Barcode child table
            exists = frappe.db.exists("Item Barcode", {"barcode": candidate})
            if not exists:
                barcode_number = candidate
                break  # Found a unique barcode

        # Generate barcode image using BarcodeAPI.org
        try:
            # Use BarcodeAPI.org to generate EAN-13 barcode with increased spacing
            api_url = f"https://barcodeapi.org/api/ean13/{barcode_number}?height=20&width=3&margin=10"
            
            # Make request to BarcodeAPI.org
            response = requests.get(api_url, stream=True)
            
            if response.status_code == 200:
                # Create File document in Frappe with the downloaded image
                file_doc = frappe.get_doc({
                    "doctype": "File",
                    "file_name": f"barcode_ean13_{item.name}_{barcode_number}.png",
                    "content": response.content,
                    "decode": False,
                    "is_private": 0,
                    "folder": "Home/Attachments"
                })
                file_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                
                # Get the file URL
                barcode_url = file_doc.file_url
            else:
                frappe.log_error(f"BarcodeAPI.org request failed for item {item.name}: HTTP {response.status_code}")
                barcode_url = None
                
        except Exception as e:
            frappe.log_error(f"Error generating barcode image for item {item.name}: {str(e)}")
            barcode_url = None

        # Append to child table with barcode URL and EAN-13 type
        doc.append("barcodes", {
            "barcode": barcode_number,
            "barcode_type": "EAN",
            "barcode_url": barcode_url
        })

        # Save the item
        doc.flags.ignore_mandatory = True
        doc.save()

    frappe.db.commit()
    return "Unique EAN-13 barcodes with images generated for items without barcodes."

@frappe.whitelist()
def generate_barcode_after_save(doc, method=None):
    
    barcode_number = None
    while True:
        # Generate a valid EAN-13 number
        candidate = generate_valid_ean13()

        # Check if barcode exists in Item Barcode child table
        exists = frappe.db.exists("Item Barcode", {"barcode": candidate})
        if not exists:
            barcode_number = candidate
            break  # Found a unique barcode

    # Generate barcode image using BarcodeAPI.org
    try:
        # Use BarcodeAPI.org to generate EAN-13 barcode with increased spacing
        api_url = f"https://barcodeapi.org/api/ean13/{barcode_number}?height=100&width=3&margin=10"
        
        # Make request to BarcodeAPI.org
        response = requests.get(api_url, stream=True)
        
        if response.status_code == 200:
            # Create File document in Frappe with the downloaded image
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f"barcode_ean13_{doc.name}_{barcode_number}.png",
                "content": response.content,
                "decode": False,
                "is_private": 0,
                "folder": "Home/Attachments"
            })
            file_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # Get the file URL
            barcode_url = file_doc.file_url
        else:
            frappe.log_error(f"BarcodeAPI.org request failed for item {doc.name}: HTTP {response.status_code}")
            barcode_url = None
            
    except Exception as e:
        frappe.log_error(f"Error generating barcode image for item {doc.name}: {str(e)}")
        barcode_url = None

    # Append to child table with barcode URL and EAN-13 type
    doc.append("barcodes", {
        "barcode": barcode_number,
        "barcode_type": "EAN",
        "barcode_url": barcode_url
    })

    # Save the item
    doc.flags.ignore_mandatory = True
    doc.save()

    frappe.db.commit()

@frappe.whitelist()
def update_deposit():
    # Define the batches with their system and paper values
    batches = [
        {"name": "Batch 1  - Serekunda",  "system": 248548, "paper": 1360500},
        {"name": "Batch 2  - Serekunda",  "system": 493520, "paper": 975550},
        {"name": "Batch 3 - Serekunda",  "system": 262995, "paper": 1621600},
        {"name": "Batch 5 - Serekunda",  "system": 461025, "paper": 953230},
        {"name": "Foni Batch - Foni",  "system": 83615, "paper": 280950},
        {"name": "Basse Batch - Basse",  "system": 38255, "paper": 301690},
        {"name": "Farafenni",  "system": 24150, "paper": 117610}
    ]
    
    # Names to use for random customer generation
    first_names = ["Ebrima", "Fatou", "Isatou", "Momodou", "Alieu", "Awa", "Lamin", "Maimuna", "Abdoulie", "Kumba"]
    last_names = ["Jallow", "Camara", "Ceesay", "Touray", "Sowe", "Njie", "Darboe", "Bah", "Jammeh", "Saidy"]
    
    # Branch options
    branches = ["Njie Charakh World Market 1", "Njie Charakh World Market 2"]
    
    # Date range from January 2023 to current date
    end_date = datetime.now().date()
    start_date = datetime(2023, 1, 1).date()
    
    results = []
    
    for batch in batches:
        # Calculate the exact shortfall we need to add
        shortfall = batch["paper"] - batch["system"]
        
        if shortfall <= 0:
            results.append(f"No shortfall for {batch['name']}")
            continue
        
        # Show the exact amount we're going to add
        results.append(f"Adding {shortfall} to {batch['name']} (System: {batch['system']}, Paper: {batch['paper']})")
        
        # Define deposit limits based on typical transaction sizes
        min_deposit = 100  # Minimum deposit amount
        max_deposit = 3000  # Maximum deposit amount
        
        # Track how much we've added so far
        added_so_far = 0
        
        # Generate random deposits until we reach EXACTLY the shortfall
        while added_so_far < shortfall:
            # Calculate remaining amount to add
            remaining = shortfall - added_so_far
            
            # For the last deposit (or if remaining is small), use exact remaining amount
            if remaining <= max_deposit:
                # If we're close to the end, just add the exact remaining amount
                amount = remaining
            else:
                # Otherwise generate a random amount
                amount = random.randint(min_deposit, max_deposit)
                
                # Make sure we don't exceed the shortfall
                if added_so_far + amount > shortfall:
                    amount = shortfall - added_so_far
            
            # Generate a random customer
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            customer_name = f"{first_name} {last_name}"
            
            # Generate a random phone number
            first_digit = random.choice(['7', '2', '3', '5', '6', '9', '4'])
            remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            phone_number = f"+220{first_digit}{remaining_digits}"
            
            # Assign branch randomly
            branch = random.choice(branches)
            
            # Generate a random date between Jan 2023 and now
            random_days = random.randint(0, (end_date - start_date).days)
            posting_date = start_date + timedelta(days=random_days)
            
            # Create customer if not exists
            customer_exists = frappe.db.exists("Customer", {"phone_number": phone_number})
            if not customer_exists:
                customer = frappe.new_doc("Customer")
                customer.customer_name = customer_name
                customer.phone_number = phone_number
                customer.custom_branch = branch
                customer.custom_batch = batch["name"]
                customer.to_be_deleted = 1
                customer.insert(ignore_permissions=True)
                frappe.db.commit()
            else:
                customer = frappe.get_doc("Customer", {"phone_number": phone_number})
            
            # Create deposit transaction
            update_deposits(customer.name, amount, posting_date)
            
            # Update the running total we've added
            added_so_far += amount
            
            results.append(f"Created deposit of {amount} for {customer_name} in {batch['name']} (Total added: {added_so_far}/{shortfall})")
        
        # Double-check that we've added exactly the shortfall amount
        assert added_so_far == shortfall, f"Added {added_so_far} but shortfall was {shortfall}"
    
    return "\n".join(results)

def update_deposits(customer, amount, posting_date):
    """Create a deposit transaction for a customer"""
    customer_doc = frappe.get_doc("Customer", customer)
    
    transaction = frappe.new_doc("Deposit")
    transaction.date = posting_date
    transaction.amount = amount
    transaction.customer = customer
    transaction.insert(ignore_permissions=True)
    
    frappe.db.commit()
    return transaction.name
    
@frappe.whitelist()
def submit():
    # docs = frappe.get_all("Deposit", {"docstatus": 0})
    # for doc in docs:
    #     doc.submit()
    # frappe.db.commit()
    # return "Success"
    frappe.db.sql("UPDATE `tabDeposit` SET docstatus = 1")
    frappe.db.commit()
    return "Success"

@frappe.whitelist()
def test_barcode_creation():
    # Check how many items exist
    items_count = frappe.db.count("Item")
    
    # Check how many item barcodes exist
    barcodes_count = frappe.db.count("Item Barcode")
    
    # Get a sample of items with barcodes
    sample_barcodes = frappe.db.sql("""
        SELECT i.name as item_name, ib.barcode, ib.barcode_type, ib.barcode_url
        FROM `tabItem` i
        JOIN `tabItem Barcode` ib ON ib.parent = i.name
        LIMIT 5
    """, as_dict=True)
    
    # Check files created
    files_count = frappe.db.count("File", {"file_name": ["like", "%barcode_ean13%"]})
    
    return {
        "items_count": items_count,
        "barcodes_count": barcodes_count,
        "sample_barcodes": sample_barcodes,
        "barcode_files_count": files_count
    }

@frappe.whitelist()
def create_test_items():
    """Create some test items to test barcode generation"""
    test_items = [
        {"item_code": "TEST-001", "item_name": "Test Product 1", "item_group": "Products"},
        {"item_code": "TEST-002", "item_name": "Test Product 2", "item_group": "Products"},
        {"item_code": "TEST-003", "item_name": "Test Product 3", "item_group": "Products"},
    ]
    
    created_items = []
    
    for item_data in test_items:
        # Check if item already exists
        if not frappe.db.exists("Item", item_data["item_code"]):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": item_data["item_code"],
                "item_name": item_data["item_name"],
                "item_group": item_data["item_group"],
                "stock_uom": "Nos",
                "is_stock_item": 1
            })
            item.insert(ignore_permissions=True)
            created_items.append(item_data["item_code"])
    
    frappe.db.commit()
    return f"Created {len(created_items)} test items: {', '.join(created_items)}"

