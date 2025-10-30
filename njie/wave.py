import frappe
import requests
import json
import uuid
from datetime import datetime
from frappe import _

config = frappe.get_site_config()
WAVE_API_KEY = config.get("wave", {}).get("api_key")

def _generate_idempotency_key():
    """Generate a unique idempotency key for Wave API requests"""
    return str(uuid.uuid4())

def _get_wave_headers(api_key, idempotency_key=None):
    """Get standard headers for Wave API requests"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


@frappe.whitelist(allow_guest=True)
def create_payout(amount, phone, name=None, client_reference=None,
                  national_id=None, payment_reason=None, currency="GMD"):
    """
    Create a single payout to send money to a recipient

    Args:
        amount (str): The amount to be paid out (net of fees)
        mobile (str): Recipient's phone number in E.164 format (e.g., +221555110219)
        name (str, optional): Recipient's name for verification
        client_reference (str, optional): Unique reference for correlation
        national_id (str, optional): Recipient's national ID for verification
        payment_reason (str, optional): Reason for payment (max 40 chars)
        currency (str): Currency code (default: GMD)

    Returns:
        dict: Payout result with status and details
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Generate idempotency key for safe retries
        idempotency_key = _generate_idempotency_key()
        mobile = f"+220{phone}"

        # Prepare the payout payload
        payout_data = {
            "currency": currency,
            "receive_amount": str(amount),
            "mobile": mobile,
        }

        # Add optional fields if provided
        if name:
            payout_data["name"] = name
        if client_reference:
            payout_data["client_reference"] = client_reference
        if national_id:
            payout_data["national_id"] = national_id
        if payment_reason:
            payout_data["payment_reason"] = payment_reason

        # Make API call to Wave to create payout
        url = "https://api.wave.com/v1/payout"
        headers = _get_wave_headers(api_key, idempotency_key)

        response = requests.post(url, json=payout_data, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            # Payout created successfully
            payout_id = response_data.get("id")

            # Store payout info for tracking
            frappe.cache().set_value(
                f"wave_payout_{payout_id}",
                {
                    "amount": amount,
                    "mobile": mobile,
                    "name": name,
                    "client_reference": client_reference,
                    "status": response_data.get("status"),
                    "created_at": frappe.utils.now(),
                },
                expires_in_sec=86400,  # 24 hours
            )

            return {
                "success": True,
                "payout_id": payout_id,
                "status": response_data.get("status"),
                "fee": response_data.get("fee"),
                "timestamp": response_data.get("timestamp"),
                "client_reference": client_reference,
            }
        else:
            # Handle API errors
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                frappe.get_traceback(),
                "Wave Payout Creation Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_payout(payout_id):
    """
    Retrieve a single payout by ID

    Args:
        payout_id (str): The payout ID (starts with pt-)

    Returns:
        dict: Payout details and status
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Make API call to retrieve payout
        url = f"https://api.wave.com/v1/payout/{payout_id}"
        headers = _get_wave_headers(api_key)

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return {
                "success": True,
                "payout": response_data,
            }
        else:
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Payout Retrieval Error: {json.dumps(response_data)}",
                "Wave Payout Retrieval Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Payout Retrieval Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def search_payouts(client_reference):
    """
    Search payouts by client reference

    Args:
        client_reference (str): The client reference to search for

    Returns:
        dict: List of payouts matching the reference
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Make API call to search payouts
        url = f"https://api.wave.com/v1/payouts/search?client_reference={client_reference}"
        headers = _get_wave_headers(api_key)

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return {
                "success": True,
                "payouts": response_data.get("result", []),
            }
        else:
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Payout Search Error: {json.dumps(response_data)}",
                "Wave Payout Search Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Payout Search Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def create_payout_batch(payouts_list):
    """
    Create a batch of payouts

    Args:
        payouts_list (list): List of payout objects, each containing:
            - amount (str): Amount to pay
            - mobile (str): Recipient phone number
            - name (str, optional): Recipient name
            - client_reference (str, optional): Client reference
            - national_id (str, optional): National ID
            - payment_reason (str, optional): Payment reason
            - currency (str, optional): Currency code (default: GMD)

    Returns:
        dict: Batch creation result with batch ID
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Generate idempotency key for safe retries
        idempotency_key = _generate_idempotency_key()

        # Prepare the batch payload
        batch_data = {
            "payouts": []
        }

        for payout in payouts_list:
            payout_item = {
                "currency": payout.get("currency", "GMD"),
                "receive_amount": str(payout["amount"]),
                "mobile": payout["mobile"],
            }

            # Add optional fields
            if payout.get("name"):
                payout_item["name"] = payout["name"]
            if payout.get("client_reference"):
                payout_item["client_reference"] = payout["client_reference"]
            if payout.get("national_id"):
                payout_item["national_id"] = payout["national_id"]
            if payout.get("payment_reason"):
                payout_item["payment_reason"] = payout["payment_reason"]

            batch_data["payouts"].append(payout_item)

        # Make API call to create payout batch
        url = "https://api.wave.com/v1/payout-batch"
        headers = _get_wave_headers(api_key, idempotency_key)

        response = requests.post(url, json=batch_data, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            batch_id = response_data.get("id")

            # Store batch info for tracking
            frappe.cache().set_value(
                f"wave_batch_{batch_id}",
                {
                    "payouts_count": len(payouts_list),
                    "status": "processing",
                    "created_at": frappe.utils.now(),
                },
                expires_in_sec=86400,  # 24 hours
            )

            return {
                "success": True,
                "batch_id": batch_id,
            }
        else:
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Payout Batch Error: {json.dumps(response_data)}",
                "Wave Payout Batch Creation Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Payout Batch Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_payout_batch(batch_id):
    """
    Retrieve a payout batch by ID

    Args:
        batch_id (str): The batch ID (starts with pb-)

    Returns:
        dict: Batch details and individual payout statuses
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Make API call to retrieve batch
        url = f"https://api.wave.com/v1/payout-batch/{batch_id}"
        headers = _get_wave_headers(api_key)

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return {
                "success": True,
                "batch": response_data,
            }
        else:
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Payout Batch Retrieval Error: {json.dumps(response_data)}",
                "Wave Payout Batch Retrieval Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Payout Batch Retrieval Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def reverse_payout(payout_id):
    """
    Reverse a previously executed payout

    Args:
        payout_id (str): The payout ID to reverse

    Returns:
        dict: Reversal result
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Generate idempotency key for safe retries
        idempotency_key = _generate_idempotency_key()

        # Make API call to reverse payout
        url = f"https://api.wave.com/v1/payout/{payout_id}/reverse"
        headers = _get_wave_headers(api_key, idempotency_key)

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            # Update cache to reflect reversal
            cache_key = f"wave_payout_{payout_id}"
            payout_cache = frappe.cache().get_value(cache_key) or {}
            payout_cache["status"] = "reversed"
            payout_cache["reversed_at"] = frappe.utils.now()
            frappe.cache().set_value(cache_key, payout_cache, expires_in_sec=86400)

            return {
                "success": True,
                "message": "Payout reversed successfully",
            }
        else:
            response_data = response.json()
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Payout Reversal Error: {json.dumps(response_data)}",
                "Wave Payout Reversal Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Payout Reversal Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def check_payout_status(payout_id):
    """
    Check the status of a payout (wrapper around get_payout)

    Args:
        payout_id (str): The payout ID to check

    Returns:
        dict: Payout status and details
    """
    try:
        result = get_payout(payout_id)

        if result.get("success"):
            payout = result["payout"]
            status = payout.get("status")

            # Map Wave status to our app's status format
            status_mapping = {
                "processing": "IN_PROGRESS",
                "succeeded": "SUCCEEDED",
                "failed": "FAILED",
                "reversed": "REVERSED",
            }

            mapped_status = status_mapping.get(status, "UNKNOWN")

            return {
                "success": True,
                "status": mapped_status,
                "wave_status": status,
                "payout_id": payout_id,
                "amount": payout.get("receive_amount"),
                "fee": payout.get("fee"),
                "mobile": payout.get("mobile"),
                "timestamp": payout.get("timestamp"),
                "client_reference": payout.get("client_reference"),
                "payout_error": payout.get("payout_error"),
            }
        else:
            return result

    except Exception as e:
        frappe.log_error(f"Wave Payout Status Check Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_payout_balance():
    """
    Get the current balance of the business wallet

    Returns:
        dict: Wallet balance information
    """
    try:
        # Fetch the Wave API key from configuration
        api_key = WAVE_API_KEY
        if not api_key:
            frappe.log_error("Wave API Key not configured", "Wave Payout Error")
            return {"success": False, "message": "Wave API Key not configured"}

        # Make API call to get wallet balance
        url = "https://api.wave.com/v1/wallet"
        headers = _get_wave_headers(api_key)

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return {
                "success": True,
                "balance": response_data.get("balance"),
                "currency": response_data.get("currency"),
            }
        else:
            error_code = response_data.get("code") or response_data.get("error_code")
            error_message = response_data.get("message") or response_data.get("error_message", "Unknown error")

            frappe.log_error(
                f"Wave Balance Check Error: {json.dumps(response_data)}",
                "Wave Balance Check Failed",
            )

            return {
                "success": False,
                "error_code": error_code,
                "message": error_message
            }

    except Exception as e:
        frappe.log_error(f"Wave Balance Check Error: {str(e)}", "Wave Payout Error")
        return {"success": False, "message": str(e)}
