# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class User:
    id: int
    username: str
    discriminator: int
    flags: int
    avatar: str
    banner: str
    locale: str
    joined_at: datetime
    bio: str
    verified: bool
    system: bool
    bot: bool
    referrer: str
    pronouns: str


@dataclass
class UserE(User):
    email: str
    password: str = None


@dataclass
class Guild:
    id: int
    name: str
    vanity_url: str
    icon: str
    banner: str
    owner_id: int
    nsfw: bool
    large: bool
    perferred_locale: str
    permissions: str
    splash: str
    features: List[str]
    verified: bool


@dataclass
class Role:
    id: int
    name: str
    color: int
    hoist: bool
    icon: str
    position: int
    permissions: str
    mentionable: bool


@dataclass
class Member:
    id: int
    user: User
    avatar: str
    banner: str
    joined_at: datetime
    roles = List[str]
    nick: str
    owner: bool


@dataclass
class Invite:
    id: int
    creator_id: int
    created_at: datetime
    max_invited: int
    amount_invited: int


@dataclass
class PermissionOverwrite:
    channel_id: int
    user_id: int
    type: int
    allow: int
    deny: int


@dataclass
class Channel:
    id: int
    type: int
    position: int
    name: str
    topic: str
    slowmode_timeout: int
    parent_id: str


@dataclass
class Pin:
    channel_id: str
    message_id: str


@dataclass
class Message:
    id: str
    channel_id: str
    author_id: str
    content: str
    created_at: datetime
    last_edited: datetime
    tts: bool
    mentions_everyone: bool
    mentioned_users: List[int]
    pinned: bool
    referenced_message_id: str


@dataclass
class ReadState:
    id: int
    channel_id: str
    last_message_id: str


@dataclass
class Meta:
    user_id: str
    theme: str
    guild_placements: List[int]
    direct_message_ignored_guilds: List[int]
    developer_mode: bool


@dataclass
class GuildMeta:
    user_id: str
    guild_id: str
    muted_channels: List[int]


@dataclass
class Note:
    creator_id: str
    user_id: str
    content: str


@dataclass
class Audit:
    audited: int
    auditor: int
    type: str
    object_id: str
    postmortem: str
    audit_id: str
    audited_at: datetime


@dataclass
class Webhook:
    id: str
    channel_id: str
    creator_id: str
    name: str
    avatar: str
    token: str


@dataclass
class Error:
    code: int
    message: str
