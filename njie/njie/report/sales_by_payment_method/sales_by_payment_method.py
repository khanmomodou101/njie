# Copyright (c) 2026, khan and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "payment_method",
			"label": "Payment Method",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "transaction_count",
			"label": "Transaction Count",
			"fieldtype": "Int",
			"width": 140
		},
		{
			"fieldname": "total_amount",
			"label": "Total Amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"fieldname": "percentage",
			"label": "Percentage (%)",
			"fieldtype": "Percent",
			"width": 130
		},
		{
			"fieldname": "avg_transaction",
			"label": "Avg Transaction",
			"fieldtype": "Currency",
			"width": 150
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	result = frappe.db.sql("""
		SELECT
			drt.payment_method,
			COUNT(drt.name) as transaction_count,
			SUM(drt.amount) as total_amount
		FROM `tabDaily Record Table` drt
		INNER JOIN `tabDaily Record Sales` drs ON drs.name = drt.parent
		WHERE drs.docstatus = 1 {conditions}
		GROUP BY drt.payment_method
		ORDER BY total_amount DESC
	""".format(conditions=conditions), filters, as_dict=1)

	grand_total = sum(r.total_amount or 0 for r in result)

	data = []
	for r in result:
		total = r.total_amount or 0
		count = r.transaction_count or 0
		data.append({
			"payment_method": r.payment_method,
			"transaction_count": count,
			"total_amount": total,
			"percentage": (total / grand_total * 100) if grand_total else 0,
			"avg_transaction": (total / count) if count else 0,
		})

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " AND drs.date BETWEEN %(from_date)s AND %(to_date)s"
	if filters.get("machine"):
		conditions += " AND drs.machine = %(machine)s"
	return conditions


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["payment_method"] for d in data],
			"datasets": [
				{
					"name": "Total Amount",
					"values": [d["total_amount"] for d in data]
				}
			]
		},
		"type": "pie",
	}
