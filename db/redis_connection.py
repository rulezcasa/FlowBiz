import redis

# --- Session ---
redisSession = redis.Redis(
    host='redis-12104.crce281.ap-south-1-3.ec2.cloud.redislabs.com',
    port=12104,
    password="flowbiz@123",
    decode_responses=True
)


