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
import grpcinsurer_pb2
import grpcinsurer_pb2_grpc

import aiohttp
import settings
import sys

_cleanup_coroutines = []
_control_execution = True

class GRPCInsurer(grpcinsurer_pb2_grpc.GRPCInsurerServicer):
    async def GetContactAndPoliciesById(
            self, request: grpcinsurer_pb2.UserRequest,
            context: grpc.aio.ServicerContext) -> grpcinsurer_pb2.PolicyHolderResponse:

        # Test data
        # request.id
        policies = []
        policies.append(grpcinsurer_pb2.Policy(mobile_number="111111111", premium=2000,type="homeowner"))
        policies.append(grpcinsurer_pb2.Policy(mobile_number="222222222", premium=1000,type="personal_auto"))
        policy_holder = grpcinsurer_pb2.PolicyHolderResponse(
            policy_holder=grpcinsurer_pb2.User(
                name="TestName",
                mobile_number="123456789"
                ),
            policies=policies
            )

        return policy_holder

    async def GetContactsAndPoliciesByMobileNumber(
            self, request: grpcinsurer_pb2.MobileNumberRequest,
            context: grpc.aio.ServicerContext) -> grpcinsurer_pb2.PolicyHolderResponse:
        
        # Test data
        # request.mobile_number
        policies = []
        policies.append(grpcinsurer_pb2.Policy(mobile_number="111111111", premium=2000,type="homeowner"))
        policy_holder = grpcinsurer_pb2.PolicyHolderResponse(
            policy_holder=grpcinsurer_pb2.User(
                name="TestName",
                mobile_number="123456789"
                ),
            policies=policies
            )

        return policy_holder

async def get_data_from_api():
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.REST_API_ADDRESS+'/users/0') as response:
            logging.info("Status: %s", response.status)
            logging.info("Content-type: %s", response.headers['content-type'])
            data = await response.text()
            logging.info("Data: %s", data)

async def Import():
    if _control_execution:
        await get_data_from_api()
        # Import the data periodically
        if settings.TIME > 0:
                await asyncio.sleep(settings.TIME)
                await Import()


async def serve() -> None:
    grpcinsurer_pb2_grpc.add_GRPCInsurerServicer_to_server(GRPCInsurer(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)

    logging.info("Starting server on %s", listen_addr)
    await server.start()

    logging.info("Importing data from REST API...")
    asyncio.ensure_future(Import())

    _cleanup_coroutines.append(server_graceful_shutdown())
    await server.wait_for_termination()


async def server_graceful_shutdown():
    # Shuts down the server with 5 seconds of grace period. During the
    # grace period, the server won't accept new connections and allow
    # existing RPCs to continue within the grace period.
    logging.info("Starting graceful shutdown...")
    await server.stop(5)
    logging.info("Server stopped.")

if __name__ == '__main__':
    _control_execution = True
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    server = grpc.aio.server()
    asyncio.ensure_future(serve())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _control_execution = False
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
        sys.exit()
