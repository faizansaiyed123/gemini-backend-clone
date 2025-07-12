import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from openai import OpenAI

from src.queue.queue import pop_from_queue
from src.services.tables import Tables
from src.configs.settings import settings
from src.logs.logger import log_message

# --- Setup ---

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
tables = Tables()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_openai_response(content):
    """Call OpenAI API and return response"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": content}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        log_message("error", f"OpenAI API error: {str(e)}", api_name="worker")
        return "Sorry, I encountered an error while processing your request."

# --- Worker Loop ---

def worker_loop():
    log_message("info", "Worker loop started", api_name="worker")

    while True:
        message = pop_from_queue()
        if not message:
            time.sleep(2)
            continue

        try:
            # Debug: Log the message structure
            log_message("debug", f"Processing message: {message}", api_name="worker")
            
            # Check if message is a dict and has required keys
            if not isinstance(message, dict):
                log_message("error", f"Message is not a dict: {type(message)}", api_name="worker")
                continue
                
            # Check for required fields
            required_fields = ["chatroom_id", "user_id", "content"]
            missing_fields = [field for field in required_fields if field not in message]
            
            if missing_fields:
                log_message("error", f"Missing required fields: {missing_fields}", api_name="worker")
                continue

            chatroom_id = message["chatroom_id"]
            user_id = message["user_id"]
            content = message["content"]

            log_message("info", f"Processing message for chatroom: {chatroom_id}", api_name="worker")

            ai_reply = call_openai_response(content)

            session = Session()
            try:
                session.execute(
                    insert(tables.chat_messages).values(
                        id=str(uuid.uuid4()),
                        chatroom_id=chatroom_id,
                        sender="ai",
                        content=ai_reply,
                        created_at=datetime.utcnow()
                    )
                )
                session.commit()
                log_message(
                    "success",
                    "AI message stored successfully",
                    data={
                        "chatroom_id": chatroom_id,
                        "user_id": user_id,
                        "ai_reply": ai_reply
                    },
                    api_name="worker"
                )
            except Exception as db_error:
                log_message("error", f"Database error: {str(db_error)}", api_name="worker")
                session.rollback()
            finally:
                session.close()

        except KeyError as e:
            log_message("error", f"KeyError - missing key: {str(e)}", api_name="worker")
        except Exception as e:
            log_message("error", f"Worker error: {str(e)}", api_name="worker")

# --- Entry Point ---

if __name__ == "__main__":
    worker_loop()



  