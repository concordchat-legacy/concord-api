from typing import List

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, delete, get, patch, post, put

from ..checks import get_member_permissions, validate_member, validate_user
from ..database import (
    Guild,
    GuildChannel,
    GuildInvite,
    Member,
    Message,
    UserType,
    to_dict,
)
from ..errors import BadData, Forbidden
from ..randoms import get_bucket, get_welcome_content, factory
from ..redis_manager import guild_event
from ..utils import AuthHeader, jsonify


class GuildsCore(Controller):
    @post('/guilds')
    async def create_guild(self, auth: AuthHeader, request: Request):
        # TODO: Generate a channel: "general" and category: "General" with a welcome message
        me = validate_user(auth.value, True)

        guilds = Member.objects(Member.id == me['id']).all()

        if len(guilds) == 200:
            raise BadData()

        data: dict = await request.json(orjson.loads)
        guild_id = factory().formulate()
        me_usertype = UserType(**dict(me.items()))

        inserted_data = {
            'id': guild_id,
            'name': str(data['name'])[:40],
            'description': str(data.get('description', ''))[:4000],
            'owner_id': me['id'],
            'nsfw': bool(data.get('nsfw', False)),
            'perferred_locale': me['locale'],
        }

        original_member = {
            'id': me['id'],
            'guild_id': guild_id,
            'owner': True,
            'user': me_usertype,
        }

        parent_id = factory().formulate()
        default_category_channel = {
            'id': parent_id,
            'guild_id': guild_id,
            'name': 'Text Channels',
            'parent_id': 0,
            'position': 0,
        }

        text_channel = factory().formulate()
        default_text_channel = {
            'id': text_channel,
            'guild_id': guild_id,
            'name': 'general',
            'parent_id': parent_id,
            'position': 1,
            'type': 1,
        }

        default_message = {
            'id': me['id'],
            'channel_id': text_channel,
            'bucket_id': get_bucket(text_channel),
            'guild_id': guild_id,
            'author': me_usertype,
            'content': get_welcome_content(user_id=me.id),
            'mentions': set([me_usertype]),
        }

        guild = Guild.create(**inserted_data)
        member = Member.create(**original_member, user=UserType(**dict(me)))
        channels = []
        messages = []
        channels.append(to_dict(GuildChannel.create(**default_category_channel)))
        channels.append(to_dict(GuildChannel.create(**default_text_channel)))
        messages.append(to_dict(Message.create(**default_message)))

        guild = to_dict(guild)
        member = to_dict(member)

        guild['members'] = member
        guild['channels'] = channels
        guild['messages'] = messages

        await guild_event(
            None,
            guild_id=guild['id'],
            data=guild,
            user_id=member['id'],
        )

        return jsonify(guild, 201)

    @patch('/guilds/{int:guild_id}')
    async def edit_guild(self, guild_id: int, auth: AuthHeader, request: Request):
        # TODO: Maybe bots should be able to access this?
        member, user = validate_member(
            token=auth.value, guild_id=guild_id, stop_bots=True
        )

        perms = get_member_permissions(member)

        if not perms.administator and not perms.manage_guild and not member.owner:
            raise Forbidden()

        data: dict = await request.json(orjson.loads)
        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        # TODO: Icon, Banner, Splash
        if data.get('name'):
            guild.name = str(data.pop('name'))[:40]

        if data.get('description'):
            guild.description = str(data.pop('description'))[:4000]

        if data.get('nsfw'):
            guild.nsfw = bool(data.pop('nsfw'))

        guild = guild.save()

        await guild_event(
            'EDIT',
            guild.id,
            data=to_dict(guild),
        )

        return jsonify(to_dict(guild))

    @delete('/guilds/{int:guild_id}')
    async def delete_guild(self, guild_id: int, auth: AuthHeader):
        member, user = validate_member(
            token=auth.value, guild_id=guild_id, stop_bots=True
        )

        if not member.owner:
            raise Forbidden()

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        if guild.large:
            raise Forbidden()

        guild.delete()

        members: List[Member] = Member.objects(Member.guild_id == guild_id).all()

        for member in members:
            member.delete()

        await guild_event('DELETE', guild_id=guild_id, data={'guild_id': guild.id})

        return jsonify({}, 203)

    @get('/guilds/{int:guild_id}')
    async def get_guild(self, guild_id: int, auth: AuthHeader):
        member, user = validate_member(
            token=auth.value,
            guild_id=guild_id,
        )

        guild = Guild.objects(Guild.id == member.guild_id).get()

        return jsonify(to_dict(guild))

    @put('/guilds/{int:guild_id}/vanity')
    async def claim_guild_vanity(
        self, guild_id: int, auth: AuthHeader, request: Request
    ):
        member, user = validate_member(
            token=auth.value, guild_id=guild_id, stop_bots=True
        )

        perms = get_member_permissions(member=member)

        if not perms.administator and not member.owner:
            raise Forbidden()

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        vanity_code = request.query.get('utm_vanity')[0]

        if guild.vanity_url:
            GuildInvite.objects(
                GuildInvite.id == guild.vanity_url,
                GuildInvite.guild_id == guild.id,
            ).get().delete()

        guild.vanity_url = str(vanity_code)

        GuildInvite.create(
            id=str(vanity_code),
            guild_id=guild_id,
            creator_id=0,
        )

        guild = guild.save()

        await guild_event(
            'VANITY_UPDATE',
            guild_id=guild.id,
            data={'vanity_url': guild.vanity_url},
        )

        return jsonify(to_dict(guild), 201)
