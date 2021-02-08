import json
from typing import Any, Dict
from redis import StrictRedis
from .config import CONF

redis_host_port = {
    'host': CONF.REDIS_HOST,
    'port': CONF.REDIS_PORT
}

redis_client = StrictRedis(
    **redis_host_port, charset='utf-8', decode_responses=True,
    db=CONF.REDIS_DB)


class REDIS_BASE:
    r: StrictRedis = redis_client
    prefix = __name__.split('.', 1)[0]
    my_key: str
    _key: str

    def __init__(self, my_key) -> None:
        self.my_key = my_key

    def unset_self(self) -> bool:
        self.r.delete(self._key)
        return self.r.get(self._key) is None


def needs_serialize(val):
    return isinstance(val, (dict, list, tuple, set))


class RedisDict(REDIS_BASE):

    def __init__(self, my_key) -> None:
        super().__init__(my_key)
        self._key = self.prefix + ':' + self.my_key

    def all(self) -> Dict[Any, Any]:
        key_vals = self.r.hgetall(self._key)
        if key_vals is None:
            return {}
        for k, v in key_vals.items():
            try:
                d = json.loads(v)
                assert needs_serialize(d)
                key_vals[k] = d
            except Exception:
                continue
        return key_vals

    def set(self, key, val):
        if needs_serialize(val):
            val = json.dumps(val)
        self.r.hset(self._key, key, val)

    def mset(self, mapping):
        self.r.hmset(self._key, mapping)

    def get(self, key, default=None):
        val = self.all().get(key, default)
        return val

    def remove(self, *keys):
        return self.r.hdel(self._key, *keys)
