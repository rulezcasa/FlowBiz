import redis
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") 

# --- Session ---
redisSession = redis.Redis(
    host='redis-12104.crce281.ap-south-1-3.ec2.cloud.redislabs.com',
    port=12104,
    password=REDIS_PASSWORD,
    decode_responses=True
)


