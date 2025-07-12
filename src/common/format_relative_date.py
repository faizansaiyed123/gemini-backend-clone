from datetime import datetime, timedelta
import pytz
from src.logs.logger import log_message

def format_relative_date(date: datetime) -> str:
    try:

        now = datetime.now(pytz.utc)


        if date.tzinfo is None:
            date = pytz.utc.localize(date)

        delta = now - date

        # Strip the time portion to compare only the date
        today = now.date()
        created_date = date.date()


        if created_date == today:
            return "Today"
        elif created_date == today - timedelta(days=1):
            return "Yesterday"
        elif delta.days < 7:
            return "Last Week"  
        elif delta.days < 30:
            return "Last Month"  
        elif delta.days < 365:
            # If the date is within the past year, return the full month name
            return date.strftime('%B')  # %B gives full month name (e.g., "January")
        else:
            # If the date is older than a year, return the full date in the format "Month Day, Year"
            return date.strftime('%b %d, %Y')  # Example: "Mar 25, 2025"
    
    except Exception as e:
        log_message("error", f"Error in formatting date: {str(e)}", exception=e)
        return "Invalid Date"  
