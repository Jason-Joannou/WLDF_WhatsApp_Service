from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SQLAEnum, ForeignKey
from sqlalchemy.ext.mutable import MutableDict, MutableList
from src.models.enums import ConversationState, UserType
from extentions import db

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    user_type = Column(SQLAEnum(UserType), default=UserType.UNKNOWN)
    current_state = Column(SQLAEnum(ConversationState), default=ConversationState.START)
    state_data = Column(MutableDict.as_mutable(JSON), default=dict)
    state_history = Column(MutableList.as_mutable(JSON), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', back_populates='conversations')

    def update_state(self, new_state: ConversationState):
        """Update conversation state and maintain history"""
        if self.current_state != new_state:
            self.state_history.append(self.current_state)
            self.current_state = new_state
            self.last_interaction = datetime.utcnow()

    def go_back(self) -> Optional[ConversationState]:
        """Return to previous state"""
        if self.state_history:
            previous_state = self.state_history.pop()
            self.current_state = previous_state
            self.last_interaction = datetime.utcnow()
            return previous_state
        return None