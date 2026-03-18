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
			"fieldname": "month",
			"label": "Month",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "total_records",
			"label": "Total Records",
			"fieldtype": "Int",
			"width": 120
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
			"fieldname": "net_balance",
			"label": "Net Balance",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "growth",
			"label": "Growth (%)",
			"fieldtype": "Percent",
			"width": 120
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	months = frappe.db.sql("""
		SELECT
			DATE_FORMAT(drs.date, '%%Y-%%m') as month_key,
			DATE_FORMAT(drs.date, '%%b %%Y') as month,
			COUNT(drs.name) as total_records,
			SUM(drs.total) as total_sales,
			SUM(drs.total_cash) as total_cash,
			SUM(drs.total_wave) as total_wave,
			SUM(drs.total_aps) as total_aps,
			SUM(drs.total_expenses) as total_expenses,
			SUM(drs.remaining_balance) as net_balance
		FROM `tabDaily Record Sales` drs
		WHERE drs.docstatus = 1 {conditions}
		GROUP BY month_key, month
		ORDER BY month_key ASC
	""".format(conditions=conditions), filters, as_dict=1)

	# Calculate month-over-month growth
	data = []
	prev_sales = None
	for m in months:
		total_sales = m.total_sales or 0
		growth = 0
		if prev_sales is not None and prev_sales > 0:
			growth = ((total_sales - prev_sales) / prev_sales) * 100

		data.append({
			"month": m.month,
			"total_records": m.total_records or 0,
			"total_sales": total_sales,
			"total_cash": m.total_cash or 0,
			"total_wave": m.total_wave or 0,
			"total_aps": m.total_aps or 0,
			"total_expenses": m.total_expenses or 0,
			"net_balance": m.net_balance or 0,
			"growth": growth if prev_sales is not None else 0,
		})
		prev_sales = total_sales

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
			"labels": [d["month"] for d in data],
			"datasets": [
				{"name": "Sales", "values": [d["total_sales"] for d in data]},
				{"name": "Expenses", "values": [d["total_expenses"] for d in data]},
			]
		},
		"type": "line",
	}
