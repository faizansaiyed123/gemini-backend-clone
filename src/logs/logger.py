import os
import csv
import sys
import inspect
import functools
from datetime import datetime
from loguru import logger
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session


LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


ERROR_LOG_FILE = os.path.join(LOG_DIR, f"error_logs_{datetime.now().strftime('%Y-%m-%d')}.csv")


logger.remove()
logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
logger.add(ERROR_LOG_FILE, format="{time} | {level} | {message}", level="ERROR", rotation="1 day") 


if not os.path.exists(ERROR_LOG_FILE) or os.path.getsize(ERROR_LOG_FILE) == 0:
    with open(ERROR_LOG_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "api_name", "level", "message", "data", "exception"])
        writer.writeheader()

#  Helper Function to Log with Auto API Name, Data, & Exception Details
def log_message(level: str, message: str = None, data=None, exception: Exception = None, api_name: str = None):
    """
    Logs a message to both the terminal (Loguru) and a CSV file.
    :param level: Log level ('info', 'warning', 'error').
    :param message: The log message (optional).
    :param data: Optional data to log.
    :param exception: Optional exception to log.
    :param api_name: API name to log (passed dynamically).
    """

    if not message:
        message = "No message provided"

    # If API name isn't provided, fallback to function name of the caller
    if not api_name:
        api_name = inspect.stack()[1].function
    

    exception_details = None
    if exception:
        exception_details = str(exception) if isinstance(exception, Exception) else str(exception)
        exception_details = exception_details.split("\n")[0]

    if level == "info":
        logger.info(f"API: {api_name} | {message} | Data: {data}")
    elif level == "warning":
        logger.warning(f"API: {api_name} | {message} | Data: {data}")
    elif level == "error":
        logger.error(f"API: {api_name} | {message} | Data: {data} | Exception: {exception_details}")


    try:
        with open(ERROR_LOG_FILE, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp", "api_name", "level", "message", "data", "exception"])
            writer.writerow({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api_name": api_name,
                "level": level.upper(),
                "message": message,
                "data": str(data) if data else "None",
                "exception": exception_details if exception else "None"
            })
    except Exception as e:
        logger.error(f"Failed to write to CSV: {str(e).splitlines()[0]}")





# Decorator to capture API function name dynamically and log only the API name
def capture_api_name(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        api_name = kwargs.get('api_name', func.__name__)  # If API name exists in kwargs, use it
        
        message = f"API called: {api_name}" if api_name else "API called: Unknown"
        
        # Log the API call with the message 'API called: {api_name}'
        log_message("info", message, data={"user_id": kwargs.get('user_id')}, api_name=api_name)
        
        # Call the original function
        return await func(*args, **kwargs)

    return wrapper
