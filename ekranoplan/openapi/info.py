# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from blacksheep.server.openapi.common import (
    ContentInfo,
    EndpointDocs,
    ParameterInfo,
    ParameterSource,
    RequestBodyInfo,
    ResponseInfo,
)

from .examples import baddata, make_user
from .inputs import UserCreate
from .responses import UserE

create_user = EndpointDocs(
    'Creates a new Concord User',
    description='Creates a new User with the information specified.',
    responses={
        200: ResponseInfo(
            'Returns the User Created.',
            content=[ContentInfo(UserE, examples=[make_user])],
        ),
        403: baddata,
    },
)

get_user = EndpointDocs()

get_me = EndpointDocs()
