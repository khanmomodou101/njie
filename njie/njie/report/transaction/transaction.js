// Copyright (c) 2024, khan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Transaction"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("Date"),
			"fieldtype": "Date",	
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",	
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "customer_name",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",

		},
		
		{
			"fieldname": "transaction_type",
			"label": __("Transaction Type"),
			"fieldtype": "Select",
			"options": ["Deposit", "Withdrawal", "Credit", "Credit Payment"],
		}

	]
};
