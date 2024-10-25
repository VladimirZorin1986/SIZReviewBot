class CacheError(Exception):
    pass


class InvalidVariable(CacheError):
    pass


class InvalidItems(CacheError):
    pass


class ItemNotFound(CacheError):
    pass
