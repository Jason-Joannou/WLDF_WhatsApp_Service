from flask import Blueprint, request
from src._utils.twilio_client import TwilioClient
from src.database.database_factory import DatabaseFactory
from src._utils.conversation_manager import ConversationManager
from src._utils.helper import format_number
from dotenv import load_dotenv
import os

load_dotenv()

whatsapp_bp = Blueprint("whatsapp", __name__)

BASE_ROUTE = "/whatsapp"

@whatsapp_bp.route(BASE_ROUTE, methods=["POST"])
async def whatsapp() -> str:
    db_session = DatabaseFactory.create_database(
    db_type=os.getenv("DATABASE_TYPE"),
    connection_params=os.getenv("DATABASE_URL"))

    conversation_manager = ConversationManager(db_session)
    incoming_msg = request.values.get("Body", "")
    from_number = request.values.get("From", "")
    formatted_number = format_number(from_number=from_number)
    
    async with db_session() as session:
        async with session.begin():
            conversation_manager = ConversationManager(session)
            response = await conversation_manager.handle_message(formatted_number, incoming_msg)
            
            return await TwilioClient().send_template_message(
                to=from_number, 
                state=response
            )
