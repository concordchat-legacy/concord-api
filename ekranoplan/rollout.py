# Copyright 2021 Concord, Inc.
# See LICENSE for more information.

from .errors import NotFound

# rollouts are separated inside of "buckets",
# only a certain amount of buckets will get the chance to do a feature.
curves = {
    1: 10,
    2: 20,
    3: 40,
    4: 80,
    5: 160
}

rollouts = {
}


def can_use_feature(guild_id: int, rollout_id: int, curve_id: int):
    f = (guild_id >> 22) % curves[curve_id]

    a = rollouts[rollout_id]

    if f not in a:
        raise NotFound()
