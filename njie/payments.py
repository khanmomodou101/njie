import json
from typing import Any, Dict, Optional

import frappe


SUPPORTED_PROVIDERS = {"wave", "qmoney", "afrimoney"}


def _bad_request(message: str, http_status: int = 400):
    frappe.local.response["http_status_code"] = http_status
    frappe.local.response["message"] = message
    return


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_payment_link():
    try:
        try:
            data = frappe.request.get_json(silent=True) or {}
        except Exception:
            data = frappe.local.form_dict or {}

        amount = data.get("amount")
        provider = (data.get("provider") or "").strip().lower()
        # Force GMD regardless of client input
        currency = "GMD"
        reference = (data.get("reference") or "").strip() or None

        # Validate
        try:
            amount_num = float(amount)
        except Exception:
            return _bad_request("Invalid amount")

        if amount_num <= 0:
            return _bad_request("Amount must be greater than 0")

        if provider not in SUPPORTED_PROVIDERS:
            return _bad_request("Unsupported provider")

        api_base: Optional[str] = getattr(frappe.conf, "jokoor_api_base_url", None)
        api_key: Optional[str] = getattr(frappe.conf, "jokoor_api_key", None)

        if not api_base or not api_key:
            return _bad_request("Jokoor API not configured")

        # Build payload; assume smallest unit (e.g., cents) for amount
        amount_minor = int(round(amount_num * 100))
        payload: Dict[str, Any] = {
            "amount": amount_minor,
            "currency": currency,
            "provider": provider,
        }
        if reference:
            payload["reference"] = reference

        # HTTP request
        import requests  # import here to avoid module load overhead if unused

        url = f"{api_base.rstrip('/')}/payments/links"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=20)

        # Raise for HTTP errors to catch below
        try:
            resp.raise_for_status()
        except Exception:
            # Try to bubble up error message from body
            try:
                body = resp.json()
                message = body.get("message") or body.get("error") or json.dumps(body)
            except Exception:
                message = resp.text or "Upstream error"
            return _bad_request(f"Jokoor error: {message}")

        # Extract link
        try:
            body = resp.json() or {}
        except Exception:
            return _bad_request("Invalid response from Jokoor")

        link: Optional[str] = None
        # Common shapes: { data: { payment_url } } or { link } or { url }
        if isinstance(body, dict):
            if "data" in body and isinstance(body["data"], dict):
                link = (
                    body["data"].get("payment_url")
                    or body["data"].get("link")
                    or body["data"].get("url")
                )
            link = (
                link or body.get("payment_url") or body.get("link") or body.get("url")
            )

        if not link:
            return _bad_request("Payment link not found in Jokoor response")

        return {"link": link, "provider": provider}

    except Exception as exc:
        # Avoid leaking internals; return generic error
        frappe.log_error(
            title="create_payment_link failed", message=frappe.get_traceback()
        )
        return _bad_request("Unexpected server error")
