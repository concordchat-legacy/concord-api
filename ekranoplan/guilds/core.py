# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from copy import copy
from typing import List

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, delete, get, patch, post, put

from ..checks import (
    add_guild_meta,
    audit,
    delete_all_channels,
    get_member_permissions,
    upload_image,
    validate_member,
    validate_user,
)
from ..database import (
    Guild,
    GuildChannel,
    GuildInvite,
    GuildMeta,
    Member,
    Meta,
    Role,
    _get_date,
    to_dict,
)
from ..errors import BadData, Conflict, Forbidden
from ..randoms import factory, code
from ..events import guild_event
from ..utils import AuthHeader, jsonify


class GuildsCore(Controller):
    @post('/guilds')
    async def create_guild(self, auth: AuthHeader, request: Request):
        # TODO: Generate a channel: "general" and category: "General" with a welcome message
        me = validate_user(auth.value, True)

        guilds = Member.objects(Member.id == me['id']).all()

        if len(guilds) == 300:
            raise BadData()

        data: dict = await request.json(orjson.loads)
        guild_id = factory().formulate()

        inserted_data = {
            'id': guild_id,
            'name': str(data['name'])[:40],
            'description': str(data.get('description', ''))[:4000],
            'owner_id': me['id'],
            'nsfw': bool(data.get('nsfw', False)),
            'perferred_locale': me['locale'],
        }

        if data.get('icon'):
            inserted_data["icon"] = upload_image(str(data['icon']), 'guilds')

        original_member = {
            'id': me['id'],
            'guild_id': guild_id,
            'owner': True,
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
            'name': 'GENERAL'.lower(),
            'parent_id': parent_id,
            'position': 1,
            'type': 1,
        }

        guild = Guild.create(**inserted_data)
        member = Member.create(**original_member)
        channels = []
        channels.append(to_dict(GuildChannel.create(**default_category_channel)))
        channels.append(to_dict(GuildChannel.create(**default_text_channel)))

        guild = to_dict(guild)
        member = to_dict(member)

        guild['members'] = member
        guild['channels'] = channels
        add_guild_meta(user_id=me.id, guild_id=guild_id)

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
        member, me = validate_member(
            token=auth.value, guild_id=guild_id, stop_bots=True
        )

        perms = get_member_permissions(member)

        if not perms.administator and not perms.manage_guild and not member.owner:
            raise Forbidden()

        data: dict = await request.json(orjson.loads)
        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        if data.get('name'):
            guild.name = str(data.pop('name'))[:40]

        if data.get('description'):
            guild.description = str(data.pop('description'))[:4000]

        if data.get('nsfw'):
            guild.nsfw = bool(data.pop('nsfw'))

        if data.get('icon'):
            guild.icon = upload_image(data['icon'], 'guilds')

        # TODO: Check if the user is a donator and let them change this.
        # if data.get('banner'):
        # guild.banner = upload_image(data['banner'], 'guilds')

        # if data.get('splash'):
        # guild.banner = upload_image(data['splash'], 'guilds')
        old_guild = copy(guild)

        guild = guild.save()

        pm = f'# User `{me.username}`/`{str(me.id)}` Modified the Guild on `{str(_get_date())}`\n\n'
        if guild.name != old_guild.name:
            pm += f'- The new name is `{guild.name}`, old name is `{old_guild.name}`\n'

        if guild.description != old_guild.description:
            pm += f'- The new description is `{guild.description}`, old description is `{old_guild.description}`\n'

        if guild.nsfw != old_guild.nsfw:
            if guild.nsfw is True:
                pm += f'- The Guild is now `nsfw`\n'
            else:
                pm += f'- The Guild is now not `nsfw`\n'

        if guild.icon != old_guild.icon:
            pm += (
                f'- The new Guild Icon is {guild.icon}, old one was {old_guild.icon}\n'
            )

        if guild.splash != old_guild.splash:
            pm += f'- The new Guild Splash is {guild.splash}, old one was {old_guild.splash}\n'

        await guild_event(
            'EDIT',
            guild.id,
            data=to_dict(guild),
        )

        audit(
            'GUILD_UPDATE',
            guild_id=guild_id,
            postmortem=pm,
            audited=guild_id,
            object_id=guild_id,
        )

        return jsonify(to_dict(guild))

    @delete('/guilds/{int:guild_id}')
    async def delete_guild(self, guild_id: int, auth: AuthHeader):
        member, _ = validate_member(token=auth.value, guild_id=guild_id, stop_bots=True)

        if not member.owner:
            raise Forbidden()

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        if guild.large:
            raise Forbidden()

        guild.delete()

        members: List[Member] = (
            Member.objects(Member.guild_id == guild_id).allow_filtering().all()
        )

        for member in members:
            meta: Meta = Meta.objects(Meta.user_id == member.id).get()
            meta.guild_placements.remove(guild_id)
            member.delete()

        delete_all_channels(guild_id=guild_id)

        # this isn't too efficient but theres not much else i can do
        filter = (
            GuildInvite.objects(GuildInvite.guild_id == guild_id)
            .allow_filtering()
            .all()
        )

        for obj in filter:
            obj.delete()

        roles = Role.objects(Role.guild_id == guild_id).all()

        for role in roles:
            role.delete()

        metas = (
            GuildMeta.objects(GuildMeta.guild_id == guild_id).allow_filtering().all()
        )

        for meta in metas:
            meta.delete()

        await guild_event('DELETE', guild_id=guild_id, data={'guild_id': guild.id})

        return jsonify({}, 204)

    @get('/guilds/{int:guild_id}')
    async def get_guild(self, guild_id: int, auth: AuthHeader):
        member, _ = validate_member(
            token=auth.value,
            guild_id=guild_id,
        )

        guild = Guild.objects(Guild.id == member.guild_id).get()

        return jsonify(to_dict(guild))

    @get('/guilds/{int:guild_id}/invites')
    async def get_guild_invites(self, guild_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id, stop_bots=True)

        _guild_invites = (
            GuildInvite.objects(GuildInvite.guild_id == guild_id)
            .allow_filtering()
            .all()
        )
        guild_invites = []

        for invite in _guild_invites:
            guild_invites.append(to_dict(invite))

        return jsonify(guild_invites)

    @post('/guilds/{int:guild_id}/invites')
    async def create_invite(self, guild_id: int, auth: AuthHeader, request: Request):
        m, _ = validate_member(
            token=auth.value,
            guild_id=guild_id
        )

        perms = get_member_permissions(m)

        if not perms.create_invites and not perms.administator and not m.owner:
            raise Forbidden()

        data: dict = await request.json(orjson.loads)

        if data is not None:
            ttl = data.get('ttl')
            max_users = data.get('max_users') or 0

        if ttl:
            ttl = int(ttl)

        if max_users:
            max_users = int(max_users)

        invite: GuildInvite = GuildInvite.create(
            id=code(),
            guild_id=guild_id,
            creator_id=m.id,
            max_invited=max_users,
        )

        if ttl:
            invite.ttl(ttl)

        return to_dict(invite)

    @put('/guilds/{int:guild_id}/vanity')
    async def claim_guild_vanity(
        self, guild_id: int, auth: AuthHeader, request: Request
    ):
        member, me = validate_member(
            token=auth.value, guild_id=guild_id, stop_bots=True
        )

        perms = get_member_permissions(member=member)

        if not perms.administator and not member.owner:
            raise Forbidden()

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        vanity_code = request.query.get('utm_vanity')[0]

        try:
            GuildInvite.objects(GuildInvite.id == str(vanity_code)).get()
        except:
            pass
        else:
            raise Conflict()

        guild.vanity_url = str(vanity_code).lower()

        GuildInvite.create(
            id=str(vanity_code).lower(),
            guild_id=guild_id,
            creator_id=0,
        )
        old_guild = copy(guild)

        guild = guild.save()

        await guild_event(
            'VANITY_UPDATE',
            guild_id=guild.id,
            data={'vanity_url': guild.vanity_url},
        )

        if guild.vanity_url != '':
            GuildInvite.objects(
                GuildInvite.id == guild.vanity_url.lower(),
                GuildInvite.guild_id == guild.id,
            ).get().delete()

        pm = f'# User {me.username}/{str(member.id)} Changed the Vanity\n\n'
        pm += f'- The new Vanity is {guild.vanity_url}, old Vanity was {old_guild.vanity_url}'

        audit(
            'VANITY_UPDATE',
            guild_id=guild.id,
            postmortem=pm,
            audited=guild.id,
            object_id=guild.id,
        )

        return jsonify(to_dict(guild), 201)
