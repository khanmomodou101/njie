// Copyright (c) 2024, Khan and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Transaction Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": new Date().getFullYear(),  // Use JavaScript Date object
			"reqd": 1
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "All\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": new Date().getMonth() + 1,  // Months are 0-indexed, so add 1
			"reqd": 1
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
		}
	], 
	"formatter": function(value, row, column, data, default_formatter) {
		// Call the default formatter first
		let formatted_value = default_formatter(value, row, column, data);

		if (column.fieldname === "balance" && value < 0) {
			// Apply custom styling for negative balance
			formatted_value = `<span style="color:red;">${value}</span>`;
		}
		else if (column.fieldname === "balance" && value > 0) {
			// Apply custom styling for positive balance
			formatted_value = `<span style="color:green;">${value}</span>`;
		}


		return formatted_value;
	}
};
