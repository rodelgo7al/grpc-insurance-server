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

# gRPC Client implementation

import asyncio

import grpc
import grpcinsurer_pb2
import grpcinsurer_pb2_grpc

async def run() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = grpcinsurer_pb2_grpc.GRPCInsurerStub(channel)
        response = await stub.GetContactAndPoliciesById(grpcinsurer_pb2.UserRequest(id=1))

        print("Policy Holder:")
        print(response.policy_holder)
        print("Policies:")
        print(response.policies)

    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = grpcinsurer_pb2_grpc.GRPCInsurerStub(channel)
        response = await stub.GetContactsAndPoliciesByMobileNumber(grpcinsurer_pb2.MobileNumberRequest(mobile_number="1234567890"))
        
        print("Policy Holder:")
        print(response.policy_holder)
        print("Policies:")
        print(response.policies)


if __name__ == '__main__':
    asyncio.run(run())
