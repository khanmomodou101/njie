import frappe
from njie.config import initialize_payment
from frappe.utils import random_string
from frappe.utils import cint

def get_context(context):
    context.no_cache = True
   
@frappe.whitelist(allow_guest=True)
def create_payment_link(amount, success_url, error_url):
    try:
        success_url = "https://njie.royalsmb.com//success"
        error_url = "https://njie.royalsmb.com//error"
        response = initialize_payment(cint(amount), random_string(10), success_url, error_url)
        return response
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Payment Link Error")
        return {"success": False, "message": str(e)}, 500