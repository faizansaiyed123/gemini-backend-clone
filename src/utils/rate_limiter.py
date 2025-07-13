from datetime import datetime
from src.configs.redis_config import redis_client

RATE_LIMIT = 5 

def get_redis_key(user_id: str):
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"rate_limit:{user_id}:{today}"

def check_and_increment_rate_limit(user_id: str) -> bool:
    key = get_redis_key(user_id)
    current = redis_client.get(key)
    
    if current is not None and int(current) >= RATE_LIMIT:
        return False
    
    new_count = redis_client.incr(key)
    
    if new_count == 1:
        redis_client.expire(key, 86400)
        
    return True