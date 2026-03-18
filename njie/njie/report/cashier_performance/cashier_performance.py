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
			"fieldname": "cashier",
			"label": "Cashier",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"fieldname": "total_records",
			"label": "Total Records",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "total_transactions",
			"label": "Total Transactions",
			"fieldtype": "Int",
			"width": 140
		},
		{
			"fieldname": "total_sales",
			"label": "Total Sales",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "total_cash",
			"label": "Cash",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_wave",
			"label": "Wave",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_aps",
			"label": "APS",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_expenses",
			"label": "Expenses",
			"fieldtype": "Currency",
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

	cashiers = frappe.db.sql("""
		SELECT
			IFNULL(NULLIF(drs.cashier, ''), 'Unassigned') as cashier,
			COUNT(drs.name) as total_records,
			SUM(drs.total) as total_sales,
			SUM(drs.total_cash) as total_cash,
			SUM(drs.total_wave) as total_wave,
			SUM(drs.total_aps) as total_aps,
			SUM(drs.total_expenses) as total_expenses
		FROM `tabDaily Record Sales` drs
		WHERE drs.docstatus = 1 {conditions}
		GROUP BY IFNULL(NULLIF(drs.cashier, ''), 'Unassigned')
		ORDER BY total_sales DESC
	""".format(conditions=conditions), filters, as_dict=1)

	data = []
	for c in cashiers:
		# Get transaction count for this cashier
		cashier_filter = "" if c.cashier == "Unassigned" else c.cashier
		if c.cashier == "Unassigned":
			tx_count = frappe.db.sql("""
				SELECT COUNT(drt.name) as cnt
				FROM `tabDaily Record Table` drt
				INNER JOIN `tabDaily Record Sales` drs ON drs.name = drt.parent
				WHERE drs.docstatus = 1
				AND (drs.cashier IS NULL OR drs.cashier = '')
				AND drs.date BETWEEN %(from_date)s AND %(to_date)s
				{machine_cond}
			""".format(machine_cond=" AND drs.machine = %(machine)s" if filters.get("machine") else ""),
				filters, as_dict=1
			)
		else:
			tx_count = frappe.db.sql("""
				SELECT COUNT(drt.name) as cnt
				FROM `tabDaily Record Table` drt
				INNER JOIN `tabDaily Record Sales` drs ON drs.name = drt.parent
				WHERE drs.docstatus = 1
				AND drs.cashier = %(cashier_name)s
				AND drs.date BETWEEN %(from_date)s AND %(to_date)s
				{machine_cond}
			""".format(machine_cond=" AND drs.machine = %(machine)s" if filters.get("machine") else ""),
				{**filters, "cashier_name": c.cashier}, as_dict=1
			)

		total_transactions = tx_count[0].cnt if tx_count else 0
		total_sales = c.total_sales or 0

		data.append({
			"cashier": c.cashier,
			"total_records": c.total_records or 0,
			"total_transactions": total_transactions,
			"total_sales": total_sales,
			"total_cash": c.total_cash or 0,
			"total_wave": c.total_wave or 0,
			"total_aps": c.total_aps or 0,
			"total_expenses": c.total_expenses or 0,
			"avg_transaction": (total_sales / total_transactions) if total_transactions else 0,
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
			"labels": [d["cashier"] for d in data],
			"datasets": [
				{
					"name": "Total Sales",
					"values": [d["total_sales"] for d in data]
				}
			]
		},
		"type": "bar",
	}
