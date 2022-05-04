# Copyright 2021 Redux, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import threading
import time


class SnowflakeFactory:
    def __init__(self) -> None:
        self._epoch: int = 1649325271415
        self._incrementation = 0

    def formulate(self) -> int:
        current_ms = int(time.time() * 1000)
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
