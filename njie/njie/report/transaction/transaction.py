# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "fieldname": "customer_name",
            "label": "Customer Name",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 300
        },
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 200
        },
        {
            "fieldname": "transaction_type",
            "label": "Transaction Type",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "amount",
            "label": "Amount",
            "fieldtype": "Currency",
            "width": 200
        }
    ]
    return columns

def get_data(filters):
    transactions = frappe.get_all("Transactions", filters={"date": ["between", [filters.get("from_date"), filters.get("to_date")]]}, fields=["customer_name", "date", "transaction_type", "amount"])
    data = []
    for transaction in transactions:
        if filters.get("customer_name") and filters.get("customer_name") != transaction.customer_name:
            continue
        if filters.get("transaction_type") and filters.get("transaction_type") != transaction.transaction_type:
            continue
        data.append({
            "customer_name": transaction.customer_name,
            "date": transaction.date,
            "transaction_type": transaction.transaction_type,
            "amount": transaction.amount
        })
    return data
