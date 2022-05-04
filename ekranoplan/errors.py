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
from .utils import jsonify


class Err(Exception):
    resp_type = 500
    resp_message = 'Internal Server Error'

    def _to_json(self):
        return jsonify(
            {
                'code': 0,
                'message': f'{self.resp_type}: {self.resp_message}',
            }
        )


class Forbidden(Err):
    resp_type = 403
    resp_message = 'Forbidden'


class BadData(Err):
    resp_type = 400
    resp_message = 'Bad Request'


class Unauthorized(Err):
    resp_type = 401
    resp_message = 'Unauthorized'


class NotFound(Err):
    resp_type = 404
    resp_message = 'Not Found'


class Conflict(Err):
    resp_type = 409
    resp_message = 'Conflict'
