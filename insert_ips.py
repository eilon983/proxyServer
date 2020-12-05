from src.Redis.redisEntity import RedisEntity
import random
import socket
import struct

class InsertIps(object):
    """
    just a methodic class to insert ips to redis
    """
    def insert(self):

        us = []
        il = []
        uk = []
        for x in range(10000):
            us.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))
            uk.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))
            il.append(socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))))

        cache = RedisEntity()
        cache.fill_list('us',*us)
        cache.fill_list('uk',*uk)
        cache.fill_list('il',*il)
