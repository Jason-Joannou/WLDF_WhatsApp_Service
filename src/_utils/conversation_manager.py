from enum import Enum
from datetime import datetime
from enum import Enum
from typing import Dict, Any
from extentions import db
from src.models.conversation import Conversation
from src.models.user import User
from datetime import timedelta
from src.models.enums import UserType, ConversationState
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ConversationManager:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.state_handlers = {
            ConversationState.START: self._handle_start,
            ConversationState.USER_TYPE_SELECTION: self._handle_user_type_selection,
            ConversationState.STUDIO_HEAD_MENU: self._handle_studio_head_menu,
            # ConversationState.PARENT_MENU: self._handle_parent_menu,
            # ConversationState.DANCER_MENU: self._handle_dancer_menu,
            # ConversationState.COMPETITION_REGISTRATION: self._handle_competition_registration,
            # ConversationState.DANCER_REGISTRATION: self._handle_dancer_registration,
            # ConversationState.LICENSE_RENEWAL: self._handle_license_renewal
        }

    async def get_or_create_conversation(self, phone_number: str) -> Conversation:
        """Get existing conversation or create new one"""

        user_stmt = select(User).where(User.number == phone_number)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(role=UserType.UNKNOWN.value, number=phone_number)
            self.db.add(user)
            await self.db.flush()  # Flush to get user ID but don't commit yet

        stmt = select(Conversation).where(Conversation.phone_number == phone_number)
        result = await self.db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            # Create new conversation with user relationship
            conversation = Conversation(
                phone_number=phone_number,
                current_state=ConversationState.START,
                state_data={},
                state_history=[],
                user=user  # Set the relationship directly
            )
            self.db.add(conversation)
            await self.db.commit()  # Commit both user and conversation
    
        return conversation

    async def handle_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Main message handler"""
        conversation = await self.get_or_create_conversation(phone_number)
        
        # Handle back command
        if message.lower() == "back":
            previous_state = conversation.go_back()
            if previous_state:
                await self.db.commit()
                return self._get_state_response(conversation)
        
        # Handle timeout
        if self._is_conversation_timeout(conversation):
            conversation.update_state(ConversationState.START)
            conversation.state_data = {}
            await self.db.commit()
            return {
                "template": "timeout_template",
                "data": {"phone_number": phone_number}
            }
        
        # Handle current state
        handler = self.state_handlers.get(conversation.current_state)
        if handler:
            response = handler(conversation, message)
            await self.db.commit()
            return response
        
        return {"template": "error_template", "data": {}}

    def _is_conversation_timeout(self, conversation: Conversation, timeout_minutes: int = 30) -> bool:
        """Check if conversation has timed out"""
        if not conversation.last_interaction:
            return False
        
        timeout = datetime.utcnow() - conversation.last_interaction
        return timeout.total_seconds() > (timeout_minutes * 60)

    # State Handlers
    def _handle_start(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Handle start state"""
        conversation.update_state(ConversationState.USER_TYPE_SELECTION)
        return {
            "template": "user_type_selection_template",
            "data": {"phone_number": conversation.phone_number}
        }

    def _handle_user_type_selection(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Handle user type selection"""
        message = message.lower()
        if message in [ut.value for ut in UserType]:
            conversation.user_type = UserType(message)
            
            # Set next state based on user type
            next_states = {
                UserType.STUDIO_HEAD: ConversationState.STUDIO_HEAD_MENU,
                UserType.PARENT: ConversationState.PARENT_MENU,
                UserType.DANCER: ConversationState.DANCER_MENU
            }
            
            next_state = next_states.get(conversation.user_type)
            conversation.update_state(next_state)
            
            return self._get_state_response(conversation)
        
        return {
            "template": "invalid_user_type_template",
            "data": {"phone_number": conversation.phone_number}
        }

    def _handle_studio_head_menu(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Handle studio head menu"""
        options = {
            "1": ConversationState.COMPETITION_REGISTRATION,
            "2": ConversationState.DANCER_REGISTRATION,
            "3": ConversationState.LICENSE_RENEWAL
        }
        
        if message in options:
            conversation.update_state(options[message])
            return self._get_state_response(conversation)
        
        return {
            "template": "invalid_option_template",
            "data": {"phone_number": conversation.phone_number}
        }

    def _get_state_response(self, conversation: Conversation) -> Dict[str, Any]:
        """Get response template and data for current state"""
        templates = {
            ConversationState.START: "welcome_template",
            ConversationState.USER_TYPE_SELECTION: "user_type_selection_template",
            ConversationState.STUDIO_HEAD_MENU: "studio_head_menu_template",
            ConversationState.PARENT_MENU: "parent_menu_template",
            ConversationState.DANCER_MENU: "dancer_menu_template",
            ConversationState.COMPETITION_REGISTRATION: "competition_registration_template",
            ConversationState.DANCER_REGISTRATION: "dancer_registration_template",
            ConversationState.LICENSE_RENEWAL: "license_renewal_template"
        }
        
        return {
            "template": templates.get(conversation.current_state, "error_template"),
            "data": {
                "phone_number": conversation.phone_number,
                "user_type": conversation.user_type.value,
                "state_data": conversation.state_data
            }
        }

# Utility functions
def cleanup_old_conversations():
    """Cleanup conversations that haven't been active for a while"""
    timeout = datetime.utcnow() - timedelta(days=1)
    old_conversations = Conversation.query.filter(
        Conversation.last_interaction < timeout
    ).all()
    
    for conv in old_conversations:
        db.session.delete(conv)
    
    db.session.commit()

def get_user_statistics() -> Dict[str, int]:
    """Get statistics about user types"""
    stats = {}
    for user_type in UserType:
        count = Conversation.query.filter_by(user_type=user_type).count()
        stats[user_type.value] = count
    return stats


