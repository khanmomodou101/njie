// Copyright (c) 2025, khan and contributors
// For license information, please see license.txt

frappe.query_reports["Made in Gambia"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
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
            "fieldname": "payment_status",
            "label": __("Payment Status"),
            "fieldtype": "Select",
            "options": ["", "Paid", "Unpaid"],
            "default": ""
        }
    ]
};
