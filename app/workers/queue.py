import redis
from rq import Queue

from app.core.config import settings

redis_conn = redis.Redis.from_url(settings.redis_url)
queue = Queue(settings.queue_name, connection=redis_conn)
