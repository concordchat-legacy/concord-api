# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from blacksheep.server.openapi.v3 import OpenAPIHandler
from openapidocs.v3 import Info, License

from .info import *
from .responses import *

docs = OpenAPIHandler(
    info=Info(
        'Concord API',
        version='v5',
        description='The Concord OpenAPI Documentation',
        terms_of_service='https://concord.chat/terms',
        contact='mailto:contact@concord.chat',
        license=License(
            'Mozilla Public License 2.0', 'https://www.mozilla.org/en-US/MPL/2.0/'
        ),
    ),
    ui_path='/openapi/docs',
    json_spec_path='/openapi/.json',
    yaml_spec_path='/openapi/.yaml',
)
