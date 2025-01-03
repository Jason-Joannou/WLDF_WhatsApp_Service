from flask import Blueprint, request
from src._utils.router import state_router
from src._utils.twilio_client import TwilioClient

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"


@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
async def whatsapp() -> str:
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")
    print(from_number, 'This is from number')

    state = await state_router(from_number)

    return TwilioClient().send_template_message(to=from_number, state=state)
