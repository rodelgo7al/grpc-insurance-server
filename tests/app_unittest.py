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

import sys
[sys.path.append(i) for i in ['.', '..']]

import unittest
import app.grpcinsurer_pb2 as grpcinsurer_pb2
from app.async_insurer_client import GRPCClient
from app.db_manager import DBManager
import asyncio

class AioTestCase(unittest.TestCase):
    # REF: https://stackoverflow.com/questions/23033939/how-to-test-python-3-4-asyncio-code
    def __init__(self, methodName='runTest', loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._function_cache = {}
        super(AioTestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            return self.loop.run_until_complete(func(*args, **kw))
        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr) and item.startswith('test_'):
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr

class TestMyCase(AioTestCase):

    # Call GetContactAndPoliciesById rpc method from client
    async def client_get_data_by_id(self, id):
        client = GRPCClient()
        result = await client.get_contact_and_policies_by_id(id)
        return result

    # Call GetContactsAndPoliciesByMobileNumber rpc method from client
    async def client_get_data_by_mobile(self, mobile):
        client = GRPCClient()
        result = await client.get_contact_and_policies_by_mobile(mobile)
        return result

    # Helper function to build response format
    def set_policy_holder_format(self, user, policies) -> grpcinsurer_pb2.PolicyHolderResponse:
        if user is None:
            return grpcinsurer_pb2.PolicyHolderResponse()

        policies_array = []
        for policy in policies:
            policies_array.append(grpcinsurer_pb2.Policy(
                mobile_number=policy["mobile_number"], premium=policy["premium"],type=policy["type"]))

        policy_holder = grpcinsurer_pb2.PolicyHolderResponse(
            policy_holder=grpcinsurer_pb2.User(
                name=user["name"],
                mobile_number=user["mobile_number"]
                ),
            policies=policies_array
            )
        return policy_holder

    def wipe_database(self, db_file):
        db_manager = DBManager(db_file)
        db_manager.delete_data("DELETE FROM agents;")
        db_manager.delete_data("DELETE FROM policies;")
        db_manager.delete_data("DELETE FROM users;")
        db_manager.delete_data("DELETE FROM sqlite_sequence;")
        db_manager.close()

    # Tests for the RPC methods GetContactAndPoliciesById and GetContactsAndPoliciesByMobileNumber
    async def test_rpc_methods(self):
        # ID: 1
        data = await self.client_get_data_by_id(1)
        user = {"name":"user1", "mobile_number":"1234567890"}
        policies = [{"mobile_number":"1234567890", "premium":500, "type":"personal_auto"},
                    {"mobile_number":"1234567890", "premium":2000, "type":"homeowner"}]
        policy_holder = self.set_policy_holder_format(user, policies)
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567890
        data = await self.client_get_data_by_mobile("1234567890")
        self.assertEqual(policy_holder, data)

        # ID: 2
        data = await self.client_get_data_by_id(2)
        user = {"name":"user2", "mobile_number":"1234567891"}
        policies = [{"mobile_number":"1234567891", "premium":200, "type":"renter"}]
        policy_holder = self.set_policy_holder_format(user, policies)
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567891
        data = await self.client_get_data_by_mobile("1234567891")
        self.assertEqual(policy_holder, data)

        # ID: 3
        data = await self.client_get_data_by_id(3)
        user = {"name":"user3", "mobile_number":"1234567892"}
        policies = [{"mobile_number":"1234567892", "premium":100, "type":"life"},
                    {"mobile_number":"1234567892", "premium":200, "type":"homeowner"},
                    {"mobile_number":"1234567892", "premium":1500, "type":"homeowner"}]
        policy_holder = self.set_policy_holder_format(user, policies)
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567892
        data = await self.client_get_data_by_mobile("1234567892")
        self.assertEqual(policy_holder, data)

        # ID: 4
        data = await self.client_get_data_by_id(4)
        user = {"name":"user4", "mobile_number":"1234567893"}
        policies = [{"mobile_number":"1234567893", "premium":155, "type":"personal_auto"}]
        policy_holder = self.set_policy_holder_format(user, policies)
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567893
        data = await self.client_get_data_by_mobile("1234567893")
        self.assertEqual(policy_holder, data)

        # ID: 5
        data = await self.client_get_data_by_id(5)
        user = {"name":"user5", "mobile_number":"1234567894"}
        policies = [{"mobile_number":"1234567894", "premium":1000, "type":"homeowner"}]
        policy_holder = self.set_policy_holder_format(user, policies)
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567894
        data = await self.client_get_data_by_mobile("1234567894")
        self.assertEqual(policy_holder, data)

        # ID: 6 (Doesn't exist)
        data = await self.client_get_data_by_id(6)
        policy_holder = self.set_policy_holder_format(None, [])
        self.assertEqual(policy_holder, data)
        # MOBILE_NUMBER: 1234567895 (Doesn't exist)
        data = await self.client_get_data_by_mobile("1234567895")
        self.assertEqual(policy_holder, data)

    def test_database_manager_wrong_file(self):
        with self.assertRaises(Exception):
            DBManager('no_file.db')

    def test_database_manager_create_agent(self):
        self.wipe_database('db_test.db')
        db_manager = DBManager('db_test.db')
        db_manager.create_agent("0")
        id = db_manager.fetch_data("SELECT id FROM agents")
        self.assertEqual(0, id[0][0])

        db_manager.create_agent("1")
        id = db_manager.fetch_data("SELECT id FROM agents")
        self.assertEqual([0, 1], [id[0][0], id[1][0]])
        db_manager.close()

    def test_database_manager_insert_users(self):
        self.wipe_database('db_test.db')
        db_manager = DBManager('db_test.db')
        db_manager.create_agent("0")
        users = [{'name': 'user1', 'mobile_number': '1234567890'}, 
        {'name': 'user2', 'mobile_number': '123 456 7891'}, 
        {'name': 'user3', 'mobile_number': '(123) 456 7892'}, 
        {'name': 'user4', 'mobile_number': '(123) 456-7893'}, 
        {'name': 'user5', 'mobile_number': '123-456-7894'}]

        db_manager.insert_users("0", users)
        data = db_manager.fetch_data("SELECT * FROM users")
        users = [(1, 'user1', '1234567890'), (2, 'user2', '1234567891'), (3, 'user3', '1234567892'), 
                (4, 'user4', '1234567893'), (5, 'user5', '1234567894')]
        self.assertEqual(users, data)

    def test_database_manager_insert_policies(self):
        self.wipe_database('db_test.db')
        db_manager = DBManager('db_test.db')
        db_manager.create_agent("0")

        policies = [{'mobile_number': '1234567890', 'premium': 2000, 'type': 'homeowner'}, 
        {'mobile_number': '123 456 7891', 'premium': 200, 'type': 'renter'}, 
        {'mobile_number': '123-456-7892', 'premium': 1500, 'type': 'homeowner'}, 
        {'mobile_number': '(123) 456-7893', 'premium': 155, 'type': 'personal_auto'}, 
        {'mobile_number': '123-456-7894', 'premium': 1000, 'type': 'homeowner'}, 
        {'mobile_number': '123-456-7890', 'premium': 500, 'type': 'personal_auto'}, 
        {'mobile_number': '1234567892', 'premium': 100, 'type': 'life'}, 
        {'mobile_number': '(123)456-7892', 'premium': 200, 'type': 'homeowner'}]

        db_manager.insert_policies("0", policies)
        data = db_manager.fetch_data("SELECT * FROM policies")
        policies = [(1, '1234567890', 2000, 'homeowner'), (2, '1234567891', 200, 'renter'), 
        (3, '1234567892', 1500, 'homeowner'), (4, '1234567893', 155, 'personal_auto'), 
        (5, '1234567894', 1000, 'homeowner'), (6, '1234567890', 500, 'personal_auto'), 
        (7, '1234567892', 100, 'life'), (8, '1234567892', 200, 'homeowner')]
        self.assertEqual(policies, data)

if __name__ == '__main__':
    unittest.main()
