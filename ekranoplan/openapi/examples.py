# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from datetime import datetime, timezone

from blacksheep.server.openapi.common import ContentInfo, ResponseExample, ResponseInfo

from .responses import Error, User, UserE


def get_now():
    return datetime.now(timezone.utc)


make_user = ResponseExample(
    UserE(
        11504080858968069,
        'Fredwick, 45th.',
        5673,
        1,
        '',
        '',
        'en-GB',
        get_now(),
        'I am Fredick the 45th of New York.',
        verified=False,
        system=False,
        bot=False,
        referrer='',
        pronouns='He/Him',
        email='fredwick@fredwickindustries.com',
    )
)

get_user = ResponseExample(
    User(
        11504080858968069,
        'Fredwick, 45th.',
        5673,
        1,
        '',
        '',
        'en-GB',
        get_now(),
        'I am Fredick the 45th of New York.',
        verified=False,
        system=False,
        bot=False,
        referrer='',
        pronouns='He/Him',
    )
)

get_me = ResponseExample(
    UserE(
        11504080858968069,
        'Fredwick, 45th.',
        5673,
        1,
        '',
        '',
        'en-GB',
        get_now(),
        'I am Fredick the 45th of New York.',
        verified=False,
        system=False,
        bot=False,
        referrer='',
        pronouns='He/Him',
        email='fredwick@fredwickindustries.com',
    )
)

notfound = ResponseInfo(
    'Item not found.',
    content=[
        ContentInfo(
            'The Error Info', examples=[ResponseExample(Error(0, '404: Not Found'))]
        )
    ],
)

unauthorized = ResponseInfo(
    'Not authorized to view this item.',
    content=[
        ContentInfo(
            'The Error Info', examples=[ResponseExample(Error(0, '401: Unauthorized'))]
        )
    ],
)

baddata = ResponseInfo(
    'Invalid Type, Data, or other item.',
    content=[
        ContentInfo(
            'The Error Info', examples=[ResponseExample(Error(0, '400: Bad Data'))]
        )
    ],
)
