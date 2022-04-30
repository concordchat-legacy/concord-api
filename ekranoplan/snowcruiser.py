import os
import threading
import time


class SnowflakeFactory:
    def __init__(self) -> None:
        self._epoch: int = 1649325271415
        self._incrementation = 0

    def formulate(self) -> int:
        current_ms = time.time_ns() // 1000000
        epoch = current_ms - self._epoch << 22

        epoch |= (threading.current_thread().ident % 32) << 17
        epoch |= (os.getpid() % 32) << 12

        epoch |= self._incrementation % 4096

        self._incrementation += 1

        if self._incrementation == 50000:
            self._incrementation = 0

        return epoch


if __name__ == '__main__':
    l = []
    f = SnowflakeFactory()
    while True:
        sf = f.formulate()
        if sf in l:
            print(sf, ' was duplicated')
            break
        l.append(sf)
        print(sf)
