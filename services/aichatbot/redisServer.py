import redis
from flask import current_app
from bson import ObjectId


def add_recommand_gift(user_ip, gift_ids, redis_client=None):
    if not redis_client:
        redis_client = current_app.redisClient
    redis_key = f"user:{user_ip}:recommended_gifts"

    # string_ids = [str(gift_id) for gift_id in gift_ids]
    redis_client.rpush(redis_key, *gift_ids)

    # 设置过期时间为2小时
    redis_client.expire(redis_key, 7200)


def get_recommanded_gifts(user_ip, redis_client=None):
    if not redis_client:
        redis_client = current_app.redisClient

    recommended_gifts_str = redis_client.lrange(
        f"user:{user_ip}:recommended_gifts", 0,
        -1)    # 如果第一次给这个user推荐礼物的话，会返回空列表

    return recommended_gifts_str
