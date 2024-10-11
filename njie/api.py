import frappe
from frappe.model.document import Document
import requests


def autoname(doc, method=None):
    doc.name = doc.phone_number


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