"""
QR Code Service
- Generate PromptPay QR Code for payment
- Generate product QR Code
- Verify payment slip
"""
import qrcode
import io
import base64
from decimal import Decimal
from typing import Optional
from PIL import Image


def _promptpay_checksum(data: str) -> str:
    """Calculate CRC-16/CCITT-FALSE checksum for PromptPay QR."""
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X')


def generate_promptpay_qr(
    promptpay_id: str,
    amount: Optional[Decimal] = None,
    order_ref: Optional[str] = None
) -> dict:
    """
    Generate PromptPay QR Code payload (EMVCo format).
    Returns dict with qr_data (string) and qr_image_base64.
    """
    # Clean PromptPay ID (phone or tax ID)
    pid = promptpay_id.replace("-", "").replace(" ", "")
    if pid.startswith("0") and len(pid) == 10:
        pid = "0066" + pid[1:]  # Thai mobile

    # Build EMVCo payload
    merchant_id = f"0016A000000677010111{len(pid):02d}{pid}"
    payload_body = (
        f"000201"                          # Payload Format Indicator
        f"010212"                          # Point of Initiation Method (12=dynamic)
        f"29{len(merchant_id):02d}{merchant_id}"  # Merchant Account Info
        f"5303764"                         # Transaction Currency (764=THB)
    )

    if amount is not None and amount > 0:
        amount_str = f"{amount:.2f}"
        payload_body += f"54{len(amount_str):02d}{amount_str}"

    if order_ref:
        ref_field = f"05{len(order_ref):02d}{order_ref}"
        additional = f"62{len(ref_field):02d}{ref_field}"
        payload_body += additional

    payload_body += "6304"
    checksum = _promptpay_checksum(payload_body)
    qr_data = payload_body + checksum

    # Generate QR image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "qr_data": qr_data,
        "qr_image_base64": f"data:image/png;base64,{qr_base64}",
        "amount": float(amount) if amount else None,
        "promptpay_id": promptpay_id,
    }


def generate_product_qr(product_id: str, product_code: str) -> dict:
    """Generate QR code for a product (for scanning at POS)."""
    qr_content = f"AGRIPOS:PRODUCT:{product_code}:{product_id}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=4)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return {
        "qr_data": qr_content,
        "qr_image_base64": f"data:image/png;base64,{qr_base64}",
    }
