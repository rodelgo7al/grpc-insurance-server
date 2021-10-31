#    Copyright 2021 Alberto Rodelgo

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

#  Agency Management Systems REST API

from aiohttp import web
import json

async def handle_users(request):
    agentId = request.match_info.get('agentId')
    response_obj = [
        {"name": "user1", "mobile_number": "1234567890"},
        {"name": "user2", "mobile_number": "123 456 7891"},
        {"name": "user3", "mobile_number": "(123) 456 7892"},
        {"name": "user4", "mobile_number": "(123) 456-7893"},
        {"name": "user5", "mobile_number": "123-456-7894"}
        ]
    return web.Response(text=json.dumps(response_obj))

async def handle_policies(request):
    agentId = request.match_info.get('agentId')
    response_obj = [
        {"mobile_number": "1234567890", "premium": 2000, "type": "homeowner"},
        {"mobile_number": "123 456 7891", "premium": 200, "type": "renter"},
        {"mobile_number": "123-456-7892", "premium": 1500, "type": "homeowner"},
        {"mobile_number": "(123) 456-7893",  "premium": 155, "type": "personal_auto"},
        {"mobile_number": "123-456-7894", "premium": 1000, "type": "homeowner"},
        {"mobile_number": "123-456-7890", "premium": 500, "type": "personal_auto"},
        {"mobile_number": "1234567892",  "premium": 100, "type": "life"},
        {"mobile_number": "(123)456-7892", "premium": 200, "type": "homeowner"}
        ]
    return web.Response(text=json.dumps(response_obj))

app = web.Application()
app.add_routes([web.get('/users/{agentId}', handle_users),
                web.get('/policies/{agentId}', handle_policies)])

web.run_app(app)
