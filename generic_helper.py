# Author: Dhaval Patel. Codebasics YouTube Channel

import re

def extract_session_id(session_str: str):
    match = re.search(r"/sessions/([^/]+)/contexts/", session_str)
    if match:
        return match.group(1)  # Only the session ID
    return ""

def get_str_from_food_dict(food_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
    return result

if __name__ == "__main__":
    print(get_str_from_food_dict({'Samosa': 2, 'Paneer Tikka': 1, 'Chai': 3}))
    # Example usage
    #session_str = "rojects/mira-chatbot-dbkb/agent/sessions/b6f2b7b5-76ee-5947-d9fd-c75e314c2b2f/contexts/ongoing-order"
    #session_id = extract_session_id(session_str)
    #print("Extracted Session ID:", session_id)  # Output: Extracted Session ID: 1234567890
    
    
