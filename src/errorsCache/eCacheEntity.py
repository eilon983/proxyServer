import abc
import time
from src.Redis.redisEntity import RedisEntity


class ErrorsCache(metaclass=abc.ABCMeta):
    def __init__(self, k, logger):
        self.redis = RedisEntity()
        self.in_memory = []
        self.k = k
        self.relative_time = k * 60 * 60  # k hours in miliseconds
        self.logger = logger

    def suspend_for_k_hours(self, country_code, ip):
        """
        this function get the op+cc from the report error endpoint,
        and removes the ip from list, saves it in local cache - "in_memory"
        after k hours it will be returned to the country list
        :param country_code:
        :param ip:
        :return:
        """
        f = self.redis.delete_from_list(country_code, ip)
        if f:
            error_tuple = [country_code, ip, int(time.time())]
            self.in_memory.append(error_tuple)

        return f

    def insert_back(self):
        """
        this function runs by scheduler,
        to refresh the local cache of suspended ips,
        and then returns the ips to the top of the list in redis
        :return:
        """
        self.logger.info("Refreshing suspended list")
        before_k_hours = int(time.time()) - self.relative_time
        to_insert = list(filter(lambda x: x[2] < before_k_hours, self.in_memory))
        self.logger.info(f"{len(to_insert)} ips returns to lists ")
        for x in to_insert:
            try:
                self.redis.insertToTop(x[0], x[1])
                self.logger.info(f'{x[1]} is returned to {x[0]} list')
            except Exception as e:
                self.logger.error(f'{x[1]} is NOT returned to {x[0]} list Error:{e}')

            self.in_memory.remove(x)
