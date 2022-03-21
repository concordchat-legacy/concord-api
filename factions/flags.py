import functools

def _has_flag(value: int, flag: int):
    return True if value & flag else False

class FactionFlags:
    def __init__(self, v: int):
        _flag_checker = functools.partial(_has_flag, v)
        self.verified = _flag_checker(1 << 0)

class UserFlags:
    def __init__(self, v: int):
        _flag_checker = functools.partial(_has_flag, v)
        self.verified = _flag_checker(1 << 0)
        self.early_supporter = _flag_checker(1 << 1)
