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

from app.async_insurer_client import GRPCClient
import asyncio

def show_data_by_id(client, id):
    print(f"Getting contact and policies from user with id: {id}")
    res = asyncio.run(client.get_contact_and_policies_by_id(id))
    print("Result:")
    print(res)

def show_data_by_mobile(client, number):
    print(f"Getting contact and policies from user with phone number: {number}")
    res = asyncio.run(client.get_contact_and_policies_by_mobile(number))
    print("Result:")
    print(res)

def main():
    client = GRPCClient()
    
    show_data_by_id(client, 5)
    show_data_by_mobile(client, "1234567892")

if __name__ == "__main__":
    main()