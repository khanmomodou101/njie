# Copyright (c) 2026, khan and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data, filters)
	return columns, data, None, chart


def get_columns(filters):
	group_by = filters.get("group_by")

	if group_by == "Description":
		return [
			{"fieldname": "description", "label": "Description", "fieldtype": "Data", "width": 200},
			{"fieldname": "count", "label": "Count", "fieldtype": "Int", "width": 100},
			{"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 150},
			{"fieldname": "avg_amount", "label": "Avg Amount", "fieldtype": "Currency", "width": 150},
		]
	elif group_by == "Date":
		return [
			{"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
			{"fieldname": "total_sales", "label": "Total Sales", "fieldtype": "Currency", "width": 150},
			{"fieldname": "total_expenses", "label": "Total Expenses", "fieldtype": "Currency", "width": 150},
			{"fieldname": "expense_ratio", "label": "Expense Ratio (%)", "fieldtype": "Percent", "width": 140},
		]
	else:
		return [
			{"fieldname": "record", "label": "Record", "fieldtype": "Link", "options": "Daily Record Sales", "width": 130},
			{"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
			{"fieldname": "machine", "label": "Machine", "fieldtype": "Data", "width": 120},
			{"fieldname": "cashier", "label": "Cashier", "fieldtype": "Data", "width": 130},
			{"fieldname": "description", "label": "Description", "fieldtype": "Data", "width": 200},
			{"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 130},
			{"fieldname": "remark", "label": "Remark", "fieldtype": "Data", "width": 180},
		]


def get_data(filters):
	conditions = get_conditions(filters)
	group_by = filters.get("group_by")

	if group_by == "Description":
		return frappe.db.sql("""
			SELECT
				IFNULL(NULLIF(det.description, ''), 'No Description') as description,
				COUNT(det.name) as count,
				SUM(det.amount) as total_amount,
				AVG(det.amount) as avg_amount
			FROM `tabDaily Expenses Table` det
			INNER JOIN `tabDaily Record Sales` drs ON drs.name = det.parent
			WHERE drs.docstatus = 1 {conditions}
			GROUP BY IFNULL(NULLIF(det.description, ''), 'No Description')
			ORDER BY total_amount DESC
		""".format(conditions=conditions), filters, as_dict=1)

	elif group_by == "Date":
		return frappe.db.sql("""
			SELECT
				drs.date,
				SUM(drs.total) as total_sales,
				SUM(drs.total_expenses) as total_expenses,
				CASE WHEN SUM(drs.total) > 0
					THEN (SUM(drs.total_expenses) / SUM(drs.total) * 100)
					ELSE 0
				END as expense_ratio
			FROM `tabDaily Record Sales` drs
			WHERE drs.docstatus = 1 AND drs.total_expenses > 0 {conditions}
			GROUP BY drs.date
			ORDER BY drs.date ASC
		""".format(conditions=conditions), filters, as_dict=1)

	else:
		return frappe.db.sql("""
			SELECT
				drs.name as record,
				drs.date,
				drs.machine,
				drs.cashier,
				det.description,
				det.amount,
				det.remark
			FROM `tabDaily Expenses Table` det
			INNER JOIN `tabDaily Record Sales` drs ON drs.name = det.parent
			WHERE drs.docstatus = 1 {conditions}
			ORDER BY drs.date ASC, det.idx ASC
		""".format(conditions=conditions), filters, as_dict=1)


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " AND drs.date BETWEEN %(from_date)s AND %(to_date)s"
	if filters.get("machine"):
		conditions += " AND drs.machine = %(machine)s"
	if filters.get("cashier"):
		conditions += " AND drs.cashier LIKE %(cashier_like)s"
		filters["cashier_like"] = f"%{filters.get('cashier')}%"
	return conditions


def get_chart(data, filters):
	if not data:
		return None

	group_by = filters.get("group_by")

	if group_by == "Description":
		return {
			"data": {
				"labels": [d["description"] for d in data[:10]],
				"datasets": [{"name": "Amount", "values": [d["total_amount"] for d in data[:10]]}]
			},
			"type": "bar",
		}
	elif group_by == "Date":
		return {
			"data": {
				"labels": [str(d["date"]) for d in data],
				"datasets": [
					{"name": "Sales", "values": [d["total_sales"] for d in data]},
					{"name": "Expenses", "values": [d["total_expenses"] for d in data]},
				]
			},
			"type": "line",
		}

	return None
