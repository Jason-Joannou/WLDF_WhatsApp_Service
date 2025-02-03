from enum import Enum

class UserType(str, Enum):
    STUDIO_HEAD = "studio_head"
    PARENT = "parent"
    DANCER = "dancer"
    UNKNOWN = "unknown"

class ConversationState(str, Enum):
    START = "start"
    REGISTRATION = "registration"
    USER_TYPE_SELECTION = "user_type_selection"
    STUDIO_HEAD_MENU = "studio_head_menu"
    PARENT_MENU = "parent_menu"
    DANCER_MENU = "dancer_menu"
    COMPETITION_REGISTRATION = "competition_registration"
    DANCER_REGISTRATION = "dancer_registration"
    LICENSE_RENEWAL = "license_renewal"
    END = "end"