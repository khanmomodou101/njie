// Copyright (c) 2024, khan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Credit', {
	refresh: function(frm) {
		
		if (frappe.user_roles.includes("Sales Master Manager")){
			frm.set_df_property("posting_date", "read_only", 0);
			frm.set_df_property("posting_time", "read_only", 0);
		}
	},
	// refresh: function(frm) {
		//get the total amount of the credit items
		// var total = 0;
		// $.each(frm.doc.credit_items || [], function(i, d) {
		// 	total += d.amount;
		// }
		// );
		// frm.doc.total_amount = total;
		// frm.refresh_field("total_amount");

	// },
	// total_amount: function(frm) {
	// 	//get the total amount of the credit items
	// 	var total = 0;
	// 	for (var i in frm.doc.credit_items){
	// 		total += frm.doc.credit_items[i].price;
	// 	}
	// 	frm.doc.total_amount = total;
	// 	frm.refresh_field("total_amount");
		


	// }
});
