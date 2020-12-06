import redis
import os

class RedisEntity(object):
    def __init__(self):
        self.hostname = os.environ.get('REDIS_HOSTNAME', "redis")
        self._connection = None

    @property
    def connection(self):
        """
        lazy loading, open the connection only when first accessed
        auto-recover in case the connection is lost
        :return:
        """
        try:
            self._connection.get('1')
        except:
            self._connection = redis.Redis(host=self.hostname, port=6379)
        return self._connection

    def get_from_cache(self, lst):
        """
        this function returns the first value from list,
        and then push it back to the end of the list
        :param lst:
        :return value:
        """
        return self.connection.rpoplpush(lst, lst)

    def delete_from_list(self, lst, value):
        return self.connection.lrem(lst, 0, value)

    def fill_list(self, lst_name, *values):
        self.connection.ltrim(lst_name, 0, -1)
        self.connection.lpush(lst_name, *values)

    def insert_to_top(self, lst_name, *values):
        self.connection.rpush(lst_name, *values)

