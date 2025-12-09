import frappe 
from frappe.utils import nowdate, now_datetime, getdate

@frappe.whitelist(allow_guest=True)
def webhook():
    """
    Webhook endpoint to receive payment notifications and create/update Daily Record Sales
    """
    try:
        # Get the webhook data
        data = frappe.form_dict
        
        # Log the incoming webhook for debugging (just log that we received it)
        frappe.logger().info(f"Webhook received - Type: {data.get('type')}, ID: {data.get('id')}")
        
        # Check if this is a transaction.completed event
        if data.get("type") != "transaction.completed":
            frappe.logger().info("Webhook ignored - not a transaction.completed event")
            return {"status": "ignored", "message": "Not a transaction.completed event"}
        
        # Extract payment data from the new structure
        event_object = data.get("data", {}).get("object", {})
        transaction_data = event_object.get("data", {})
        metadata = event_object.get("metadata", {})
        
        # Get amount, payment method, currency and status from transaction data
        amount = float(transaction_data.get("amount", 0))
        payment_method = transaction_data.get("payment_method", "").lower()
        currency = transaction_data.get("currency", "GMD")
        status = transaction_data.get("status", "")
        
        # Check if transaction is completed
        if status != "completed":
            frappe.logger().info(f"Transaction not completed. Status: {status}")
            return {"status": "ignored", "message": f"Transaction status is {status}, not completed"}
        
        # Get transaction ID (use the Wave transaction ID from metadata if available, otherwise use the main ID)
        payment_method_txn_id = metadata.get("payment_method_txn_id", "")
        main_txn_id = event_object.get("id", "")
        
        # For cash or when payment_method_txn_id is empty, use the main transaction ID
        if payment_method_txn_id and payment_method_txn_id.strip():
            transaction_id = payment_method_txn_id
        else:
            transaction_id = main_txn_id
        
        frappe.logger().info(f"Processing payment: Amount={amount}, Method={payment_method}, Status={status}, TxnID={transaction_id}")
        
        # Validate that we have a transaction ID and valid amount
        if not transaction_id:
            frappe.logger().error("No transaction ID found in webhook data")
            return {"status": "error", "message": "Missing transaction ID"}
        
        if amount <= 0:
            frappe.logger().error(f"Invalid amount: {amount}")
            return {"status": "error", "message": "Amount must be greater than 0"}
        
        # Check if this transaction_id already exists to prevent duplicates
        existing_transaction = frappe.db.exists(
            "Daily Record Table",
            {"transactions_id": transaction_id}
        )
        
        if existing_transaction:
            frappe.logger().info(f"Duplicate transaction detected: {transaction_id}")
            return {
                "status": "duplicate",
                "message": "Transaction already processed",
                "transaction_id": transaction_id
            }
        
        # Map payment method to the correct format (capitalize first letter)
        payment_method_map = {
            "wave": "Wave",
            "aps": "APS",
            "cash": "Cash"
        }
        payment_method_formatted = payment_method_map.get(payment_method, "Cash")
        
        # Get today's date
        today = nowdate()
        machine_name = "Terminal 1"
        
        # Check if a Daily Record Sales exists for today with Terminal 1
        existing_record = frappe.db.get_value(
            "Daily Record Sales",
            filters={
                "date": getdate(today),
                "machine": machine_name,
                "docstatus": ["<", 2]  # Exclude cancelled documents
            },
            fieldname="name"
        )
        
        if existing_record:
            # Append to existing record
            frappe.logger().info(f"Found existing record: {existing_record}")
            doc = frappe.get_doc("Daily Record Sales", existing_record)
            
            # Add new row to the records table
            doc.append("records", {
                "amount": amount,
                "payment_method": payment_method_formatted,
                "time": now_datetime().strftime("%H:%M:%S"),
                "transactions_id": transaction_id
            })
            
            # Save the document
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.logger().info(f"Payment appended to record: {existing_record}")
            
            return {
                "status": "success",
                "message": "Payment appended to existing record",
                "document": existing_record,
                "transaction_id": transaction_id
            }
        else:
            # Create new Daily Record Sales document
            frappe.logger().info(f"Creating new Daily Record Sales for {today}, Machine: {machine_name}")
            doc = frappe.get_doc({
                "doctype": "Daily Record Sales",
                "date": getdate(today),
                "machine": machine_name,
                "records": [{
                    "amount": amount,
                    "payment_method": payment_method_formatted,
                    "time": now_datetime().strftime("%H:%M:%S"),
                    "transactions_id": transaction_id
                }]
            })
            
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.logger().info(f"Created new record: {doc.name}")
            
            return {
                "status": "success",
                "message": "New Daily Record Sales created",
                "document": doc.name,
                "transaction_id": transaction_id
            }
            
    except Exception as e:
        frappe.logger().error(f"Webhook error: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Webhook Error")
        return {
            "status": "error",
            "message": str(e)
        }
    