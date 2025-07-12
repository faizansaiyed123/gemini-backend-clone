import json
import requests
from src.configs.settings import settings
from src.logs.logger import log_message

UPSTASH_URL = settings.UPSTASH_REDIS_REST_URL
UPSTASH_TOKEN = settings.UPSTASH_REDIS_REST_TOKEN

HEADERS = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}",
    "Content-Type": "application/json"
}

# THIS SHOULD BE A SIMPLE QUEUE NAME, NOT YOUR API KEY!
QUEUE_KEY = "openai_chat_queue"

def push_to_queue(message_data: dict):
    try:
        response = requests.post(
            f"{UPSTASH_URL}/lpush/{QUEUE_KEY}",
            headers=HEADERS,
            json={"value": json.dumps(message_data)}  # Serialize the dict
        )
        log_message("info", "Message pushed to Redis queue", data=message_data, api_name="queue")
    except Exception as e:
        log_message("error", f"Redis push_to_queue failed: {str(e)}", api_name="queue")

def pop_from_queue():
    try:
        response = requests.post(
            f"{UPSTASH_URL}/rpop/{QUEUE_KEY}",
            headers=HEADERS
        )
        
        # Check if request was successful
        if response.status_code != 200:
            log_message("error", f"Redis request failed with status: {response.status_code}", api_name="queue")
            return None
            
        res = response.json()
        
        # Check if we got a result
        if not res.get("result"):
            return None
            
        raw_value = res["result"]
        
        # Debug: Log the raw value and its type
        log_message("debug", f"Raw value from Redis: {raw_value} (type: {type(raw_value)})", api_name="queue")
        
        # The raw_value should be the JSON string we stored with push_to_queue
        # Parse it to get the actual message data
        message_data = json.loads(raw_value)
        
        # Debug: Log the parsed message data
        log_message("debug", f"Parsed message data: {message_data} (type: {type(message_data)})", api_name="queue")
        
        # IMPORTANT: The message_data should now be the actual dict with chatroom_id, user_id, etc.
        # If it still has a 'value' key, that means we have double-encoded JSON
        if isinstance(message_data, dict) and 'value' in message_data and len(message_data) == 1:
            # This means we have double-encoded JSON - parse the 'value' field
            log_message("debug", "Detected double-encoded JSON, parsing 'value' field", api_name="queue")
            message_data = json.loads(message_data['value'])
            log_message("debug", f"Final parsed message data: {message_data}", api_name="queue")
        
        # Verify the structure
        if not isinstance(message_data, dict):
            log_message("error", f"Parsed message is not a dict: {type(message_data)}", api_name="queue")
            return None
        
        # Check if it has the expected keys
        expected_keys = ["chatroom_id", "user_id", "content"]
        missing_keys = [key for key in expected_keys if key not in message_data]
        if missing_keys:
            log_message("error", f"Missing keys in message data: {missing_keys}", api_name="queue")
            log_message("error", f"Available keys: {list(message_data.keys())}", api_name="queue")
            return None
        
        log_message("info", "Message popped from Redis queue", data=message_data, api_name="queue")
        return message_data
        
    except json.JSONDecodeError as e:
        log_message("error", f"JSON decode error in pop_from_queue: {str(e)}", 
                   data={"raw_value": raw_value if 'raw_value' in locals() else "N/A"}, 
                   api_name="queue")
    except Exception as e:
        log_message("error", f"Redis pop_from_queue failed: {str(e)}", api_name="queue")

    return None