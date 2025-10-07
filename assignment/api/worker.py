from dotenv import load_dotenv
import os
import time
from rq import Worker, Queue
from redis import Redis
from image_generator import ImageGenerator, LocalImageGenerator
from redis.exceptions import ConnectionError
from tasks import gen_image_task, gen_local_image_task

load_dotenv(override=True)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
STORAGE_DIR = os.environ.get("IMAGE_STORAGE_DIR", "/app/images")

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}, DB: {REDIS_DB}")

# Wait for Redis to be ready
while True:
    try:
        redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        redis_conn.ping()
        break
    except ConnectionError:
        print("Waiting for Redis...")
        time.sleep(1)

queue = Queue("images", connection=redis_conn)
# image_gen = ImageGenerator(API_KEY, host=STABILITY_URL)
# local_image_gen = LocalImageGenerator(STABLE_DIFFUSION_URL)

if __name__ == "__main__":
    worker = Worker([queue])
    worker.work()
