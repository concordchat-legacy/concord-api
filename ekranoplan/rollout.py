# Copyright 2021 Concord, Inc.
# See LICENSE for more information.

from .errors import NotFound

# each guild is separated into one of these, based on its ID.
# TODO: Raise when we get to ~100,000 Guilds.
CURVE = 30

rollouts = {
    # completed rollout
    0: [i for i in range(CURVE)]
}

def can_use_feature(
    guild_id: int,
    rollout_id: int
):
    f = (guild_id >> 22) % CURVE

    a = rollouts[rollout_id]

    if f not in a:
        raise NotFound()
