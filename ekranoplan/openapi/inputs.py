# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from dataclasses import dataclass


@dataclass
class UserCreate:
    username: str
    email: str
    password: str
    bio: str = ''
    pronouns: str = ''
