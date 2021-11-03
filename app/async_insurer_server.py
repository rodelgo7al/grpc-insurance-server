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

import asyncio
import logging

import grpc
import app.grpcinsurer_pb2 as grpcinsurer_pb2
import app.grpcinsurer_pb2_grpc as grpcinsurer_pb2_grpc

import aiohttp
import settings
import json

class GRPCInsurer(grpcinsurer_pb2_grpc.GRPCInsurerServicer):
    # GRPC service with two rpc methods (GetContactAndPoliciesById and GetContactsAndPoliciesByMobileNumber)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

    def create_response(self, user) -> grpcinsurer_pb2.PolicyHolderResponse:
        # Takes the user data retrieved from the database and converts it to the response format (PolicyHolderResponse)
        user_policies = self.db_manager.fetch_data(f"SELECT * FROM policies WHERE mobile_number = '{user[2]}';")
        if user_policies:
            policies = []
            for policy in user_policies:
                policies.append(grpcinsurer_pb2.Policy(mobile_number=policy[1], premium=policy[2],type=policy[3]))

        policy_holder = grpcinsurer_pb2.PolicyHolderResponse(
            policy_holder=grpcinsurer_pb2.User(
                name=user[1],
                mobile_number=user[2]
                ),
            policies=policies
            )
        return policy_holder

    async def GetContactAndPoliciesById(
            self, request: grpcinsurer_pb2.UserRequest,
            context: grpc.aio.ServicerContext) -> grpcinsurer_pb2.PolicyHolderResponse:

        user = self.db_manager.fetch_data("SELECT * FROM users WHERE id = (?);", str(request.id))
        if user:
            policy_holder = self.create_response(user[0])
            return policy_holder
        return grpcinsurer_pb2.PolicyHolderResponse() # Empty response

    async def GetContactsAndPoliciesByMobileNumber(
            self, request: grpcinsurer_pb2.MobileNumberRequest,
            context: grpc.aio.ServicerContext) -> grpcinsurer_pb2.PolicyHolderResponse:
        user = self.db_manager.fetch_data(f"SELECT * FROM users WHERE mobile_number = '{request.mobile_number}';")
        
        if user:
            policy_holder = self.create_response(user[0])
            return policy_holder
        return grpcinsurer_pb2.PolicyHolderResponse() # Empty response

class GRPCServer:
    def __init__(self, db_manager):
        self._control_execution = False
        self._cleanup_coroutines = []
        self.server_instance = None
        self.db_manager = db_manager
        self.import_process = None

    async def get_data_from_api(self, endpoint):
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.REST_API_ADDRESS+endpoint) as response:
                logging.debug("Status: %s", response.status)
                logging.debug("Content-type: %s", response.headers['content-type'])
                text = await response.text()
                return json.loads(text)
                
    async def Import(self):
        if self._control_execution:
            logging.info("Importing data from REST API...")
            
            if not settings.AGENT_ID.isdigit():
                raise Exception("Agent ID is not a valid digit")

            users = await self.get_data_from_api('/users/'+str(settings.AGENT_ID))
            policies = await self.get_data_from_api('/policies/'+str(settings.AGENT_ID))

            self.db_manager.insert_users(settings.AGENT_ID, users)
            self.db_manager.insert_policies(settings.AGENT_ID, policies)

            logging.info("Data saved into database")

            # Import the data periodically
            if self._control_execution and settings.TIME > 0:
                    await asyncio.sleep(settings.TIME)
                    await self.Import()


    async def start(self):
        self.server_instance = grpc.aio.server()
        grpcinsurer_pb2_grpc.add_GRPCInsurerServicer_to_server(GRPCInsurer(self.db_manager), self.server_instance)
        listen_addr = 'localhost:50051'
        self.server_instance.add_insecure_port(listen_addr)

        logging.info("Starting server on %s", listen_addr)
        await self.server_instance.start()
        self._control_execution = True
        self._cleanup_coroutines.append(self.server_graceful_shutdown())

        # Run subprocess Import after starting the server
        self.import_process = asyncio.create_task(self.Import())
        def import_done_callback_exception(_fut):
            if self.import_process.exception():
                logging.info("An exception ocurred. Ending application...")
                asyncio.create_task(self.server_graceful_shutdown())
                raise self.import_process.exception()
        self.import_process.add_done_callback(import_done_callback_exception)

        await self.server_instance.wait_for_termination()

    async def server_graceful_shutdown(self):
        # Shuts down the server with 5 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        if self._control_execution: 
            self._control_execution = False

            # Stop Import process if still running
            logging.info("Stopping processes...")
            while self.import_process and not self.import_process.done():
                self.import_process.cancel()
            
            logging.info("Starting graceful shutdown...")
            await self.server_instance.stop(5)
            logging.info("Server stopped.")


