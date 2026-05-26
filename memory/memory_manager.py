import redis
import json


class MemoryManager:

    def __init__(self):

        try:

            self.redis_client = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=True
            )

            self.redis_client.ping()

            print("✓ Redis memory connected")

        except Exception as e:

            self.redis_client = None

            print(f"⚠️ Redis unavailable: {e}")

    def save_session(self, session_id, data):

        if self.redis_client:

            self.redis_client.set(
                session_id,
                json.dumps(data)
            )

    def load_session(self, session_id):

        if self.redis_client:

            data = self.redis_client.get(session_id)

            if data:

                return json.loads(data)

        return None