// Copyright (c) 2026, khan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cashier Performance"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "machine",
			"label": __("Machine"),
			"fieldtype": "Select",
			"options": ["", "Machine 1", "Machine 2", "Terminal 1"]
		}
	]
};
