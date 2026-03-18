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
			"fieldname": "machine",
			"label": "Machine",
			"fieldtype": "Data",
			"width": 140
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
			"fieldname": "avg_daily_sales",
			"label": "Avg Daily Sales",
			"fieldtype": "Currency",
			"width": 150
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

	# Get machine-level aggregates
	machines = frappe.db.sql("""
		SELECT
			drs.machine,
			COUNT(drs.name) as total_records,
			SUM(drs.total) as total_sales,
			SUM(drs.total_cash) as total_cash,
			SUM(drs.total_wave) as total_wave,
			SUM(drs.total_aps) as total_aps,
			COUNT(DISTINCT drs.date) as active_days
		FROM `tabDaily Record Sales` drs
		WHERE drs.docstatus = 1 {conditions}
		GROUP BY drs.machine
		ORDER BY total_sales DESC
	""".format(conditions=conditions), filters, as_dict=1)

	# Get transaction counts per machine
	payment_condition = ""
	if filters.get("payment_method"):
		payment_condition = " AND drt.payment_method = %(payment_method)s"

	data = []
	for m in machines:
		tx_count = frappe.db.sql("""
			SELECT COUNT(drt.name) as cnt
			FROM `tabDaily Record Table` drt
			INNER JOIN `tabDaily Record Sales` drs ON drs.name = drt.parent
			WHERE drs.docstatus = 1 AND drs.machine = %s
			AND drs.date BETWEEN %s AND %s {payment_condition}
		""".format(payment_condition=payment_condition),
			(m.machine, filters.get("from_date"), filters.get("to_date")),
			as_dict=1
		)
		total_transactions = tx_count[0].cnt if tx_count else 0
		total_sales = m.total_sales or 0
		active_days = m.active_days or 1

		data.append({
			"machine": m.machine,
			"total_records": m.total_records or 0,
			"total_transactions": total_transactions,
			"total_sales": total_sales,
			"total_cash": m.total_cash or 0,
			"total_wave": m.total_wave or 0,
			"total_aps": m.total_aps or 0,
			"avg_daily_sales": total_sales / active_days,
			"avg_transaction": (total_sales / total_transactions) if total_transactions else 0,
		})

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " AND drs.date BETWEEN %(from_date)s AND %(to_date)s"
	return conditions


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["machine"] for d in data],
			"datasets": [
				{
					"name": "Total Sales",
					"values": [d["total_sales"] for d in data]
				}
			]
		},
		"type": "bar",
	}
