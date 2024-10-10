// Copyright (c) 2024, khan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Deposit', {
	refresh: function(frm) {
		
		if (frappe.user_roles.includes("Sales Master Manager")){
			frm.set_df_property("posting_date", "read_only", 0);
			frm.set_df_property("posting_time", "read_only", 0);
		}
	},
	on_submit: function(frm) {
		frm.refresh()
	}
});
//update balance
