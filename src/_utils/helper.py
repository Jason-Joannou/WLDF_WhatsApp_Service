def format_number(from_number: str) -> str:
    split_str = from_number.split(":")
    formatted_number = split_str[1]
    return formatted_number

def prepare_number_twilio(from_number: str) -> str:
    formatted_number = "whatsapp:"+from_number
    return formatted_number