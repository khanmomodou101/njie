# Copyright (c) 2025, khan and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "fieldname": "supplier",
            "label": "Supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 200
        },
        {
            "fieldname": "payment_status",
            "label": "Payment Status",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "total_billing",
            "label": "Total Billing",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "fieldname": "paid_amount",
            "label": "Paid Amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "fieldname": "unpaid_amount",
            "label": "Unpaid Amount",
            "fieldtype": "Currency",
            "width": 200
        },
    ]
    return columns

def get_data(filters=None):
    data = []

    conditions = ["s.supplier_group = 'Made in Gambia'"]
    values = {}

    # Apply date filters
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("pi.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    # Apply payment status filter
    if filters.get("payment_status"):
        if filters["payment_status"] == "Paid":
            conditions.append("pi.outstanding_amount = 0")
        elif filters["payment_status"] == "Unpaid":
            conditions.append("pi.outstanding_amount > 0")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            s.name AS supplier,
            COALESCE(SUM(pi.grand_total), 0) AS total_billing,
            COALESCE(SUM(pi.outstanding_amount), 0) AS unpaid_amount,
            COALESCE(SUM(pi.grand_total - pi.outstanding_amount), 0) AS paid_amount,
            CASE 
                WHEN COALESCE(SUM(pi.outstanding_amount), 0) = 0 THEN 'Paid'
                ELSE 'Unpaid'
            END AS payment_status
        FROM `tabSupplier` s
        LEFT JOIN `tabPurchase Invoice` pi ON pi.supplier = s.name
        WHERE {where_clause}
        GROUP BY s.name
    """

    results = frappe.db.sql(query, values, as_dict=True)

    for row in results:
        data.append({
            "supplier": row.supplier,
            "total_billing": row.total_billing,
            "paid_amount": row.paid_amount,
            "unpaid_amount": row.unpaid_amount,
            "payment_status": row.payment_status
        })

    return data
