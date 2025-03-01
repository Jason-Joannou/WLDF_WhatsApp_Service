from enum import Enum

class UserType(str, Enum):
    STUDIO_HEAD = "studio_head"
    PARENT = "parent"
    DANCER = "dancer"
    ADMIN = "admin"
    UNKNOWN = "unknown"

class ConversationState(str, Enum):
    START = "start"
    REGISTRATION = "registration"
    USER_TYPE_SELECTION = "user_type_selection"
    STUDIO_HEAD_AUTHENTICATION = "studio_head_authentication"
    STUDIO_HEAD_MENU = "studio_head_menu"
    PARENT_MENU = "parent_menu"
    DANCER_MENU = "dancer_menu"
    COMPETITION_REGISTRATION = "competition_registration"
    DANCER_REGISTRATION = "dancer_registration"
    LICENSE_RENEWAL = "license_renewal"
    END = "end"

class Templates(str, Enum):
    # Template for unregistered and unknown role
    UNREGISTERED_SELECTION_TEMPLATE = 'HX107a155dc0472d64e9bc27b4ef3594b5'
    STUDIO_HEAD_AUTHENTICATION_TEMPLATE = "template_id"
    AUTHENTICATED_STUDIO_HEAD_MENU_TEMPLATE = "template_id"