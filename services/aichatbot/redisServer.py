import redis
from flask import current_app


def add_recommand_gift(user_ip, gift_id, redis_client=None):
    if not redis_client:
        redis_client = current_app.redisClient
    redis_key = f"user:{user_ip}:recommended_gifts"
    redis_client.rpush(redis_key, *gift_id)

    # 设置过期时间为2小时
    redis_client.expire(redis_key, 7200)


def get_recommanded_gifts(user_ip, redis_client=None):
    if not redis_client:
        redis_client = current_app.redisClient
    return redis_client.lrange(f"user:{user_ip}:recommended_gifts", 0,
                               -1)    # 如果第一次给这个user推荐礼物的话，会返回空列表
