# Copyright (c) 2026, khan and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "total_records",
			"label": "Total Records",
			"fieldtype": "Int",
			"width": 110
		},
		{
			"fieldname": "total_transactions",
			"label": "Total Transactions",
			"fieldtype": "Int",
			"width": 130
		},
		{
			"fieldname": "total_sales",
			"label": "Total Sales",
			"fieldtype": "Currency",
			"width": 140
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
			"fieldname": "remaining_balance",
			"label": "Remaining Balance",
			"fieldtype": "Currency",
			"width": 150
		},
	]


def get_data(filters):
	conditions = {"docstatus": 1}

	if filters.get("from_date") and filters.get("to_date"):
		conditions["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	if filters.get("machine"):
		conditions["machine"] = filters.get("machine")
	if filters.get("cashier"):
		conditions["cashier"] = ["like", f"%{filters.get('cashier')}%"]

	records = frappe.get_all(
		"Daily Record Sales",
		filters=conditions,
		fields=[
			"date", "total", "total_cash", "total_wave", "total_aps",
			"total_expenses", "remaining_balance"
		],
		order_by="date asc"
	)

	# Group by date
	date_map = {}
	for r in records:
		date = str(r.date)
		if date not in date_map:
			date_map[date] = {
				"date": r.date,
				"total_records": 0,
				"total_transactions": 0,
				"total_sales": 0,
				"total_cash": 0,
				"total_wave": 0,
				"total_aps": 0,
				"total_expenses": 0,
				"remaining_balance": 0,
			}
		date_map[date]["total_records"] += 1
		date_map[date]["total_sales"] += r.total or 0
		date_map[date]["total_cash"] += r.total_cash or 0
		date_map[date]["total_wave"] += r.total_wave or 0
		date_map[date]["total_aps"] += r.total_aps or 0
		date_map[date]["total_expenses"] += r.total_expenses or 0
		date_map[date]["remaining_balance"] += r.remaining_balance or 0

	# Get transaction counts per date
	for date, row in date_map.items():
		parent_names = frappe.get_all(
			"Daily Record Sales",
			filters={"docstatus": 1, "date": date},
			pluck="name"
		)
		if parent_names:
			row["total_transactions"] = frappe.db.count(
				"Daily Record Table",
				filters={"parent": ["in", parent_names]}
			)

	data = sorted(date_map.values(), key=lambda x: x["date"])
	return data
