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

import sqlite3
import re
import logging

class DBManager:
    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file)
        logging.info(f"Database {db_file} connected")

    def close(self):
        self.con.close()

    def create_agent(self, agent_id):
        cursorObj = self.con.cursor()
        cursorObj.execute('INSERT OR REPLACE INTO agents(id) VALUES(?)', agent_id)
        self.con.commit()
        cursorObj.close()

    def insert_users(self, agent_id, users):
        values = []
        values_selector = [] # Needed for the table agents_users (helps to get IDs from the new inserted data)
        for row in users:
            # Get only digits in string
            phone_only_digits = re.findall(r'\d+',row['mobile_number'])
            format_number = "".join(phone_only_digits)
            values.append((row['name'], format_number))
            values_selector.append(str(row['name'])+","+format_number)
        cursorObj = self.con.cursor()
        cursorObj.executemany('INSERT INTO users(name, mobile_number) VALUES(?, ?)', values)
        self.con.commit()
        cursorObj.close()
        self.set_agents_users(agent_id, values_selector)

    def insert_policies(self, agent_id, policies):
        values = []
        values_selector = [] # Needed for the table agents_policies (helps to get IDs from the new inserted data)
        for row in policies:
            # Get only digits in string
            phone_only_digits = re.findall(r'\d+',row['mobile_number'])
            format_number = "".join(phone_only_digits)
            values.append((format_number, row['premium'], row['type']))
            values_selector.append(format_number+","+str(row['premium'])+","+str(row['type']))
        cursorObj = self.con.cursor()
        cursorObj.executemany('INSERT INTO policies(mobile_number, premium, type) VALUES(?, ?, ?)', values)
        self.con.commit()
        cursorObj.close()
        self.set_agents_policies(agent_id, values_selector)

    def insert_agents_policies(self, agent_id, policies):
        values = []
        for id in policies:
            values.append((agent_id, id[0]))
        cursorObj = self.con.cursor()
        cursorObj.executemany('INSERT INTO agents_policies(agent_id, policy_id) VALUES(?, ?)', values)
        self.con.commit()
        cursorObj.close()

    def insert_agents_users(self, agent_id, users):
        values = []
        for id in users:
            values.append((agent_id, id[0]))
        cursorObj = self.con.cursor()
        cursorObj.executemany('INSERT INTO agents_users(agent_id, user_id) VALUES(?, ?)', values)
        self.con.commit()
        cursorObj.close()

    def set_agents_policies(self, agent_id, last_inserted_values):
        # Delete current data
        self.delete_data("DELETE FROM agents_policies WHERE agent_id = '" + agent_id + "';")
        # Get new data ids
        query = "SELECT id FROM policies WHERE mobile_number || ',' || premium || ',' || type IN ({seq})".format(
            seq=','.join(['?']*len(last_inserted_values))
        )

        policies_id = self.fetch_data(query, last_inserted_values)
        # Insert into db
        self.insert_agents_policies(agent_id, policies_id)

    def set_agents_users(self, agent_id, last_inserted_values):
        # Delete current data
        self.delete_data("DELETE FROM agents_users WHERE agent_id = '" + agent_id + "';")
        # Get new data ids
        query = "SELECT id FROM users WHERE name || ',' || mobile_number IN ({seq})".format(
            seq=','.join(['?']*len(last_inserted_values))
        )
        users_id = self.fetch_data(query, last_inserted_values)
        # Insert into db
        self.insert_agents_users(agent_id, users_id)

    def fetch_data(self, select_query, values=None):
        cursorObj = self.con.cursor()
        if values is None:
            cursorObj.execute(select_query)
        else:
            cursorObj.execute(select_query, values)

        rows = cursorObj.fetchall()
        cursorObj.close()

        return rows

    def delete_data(self, delete_query):
        cursorObj = self.con.cursor()
        cursorObj.execute(delete_query)
        self.con.commit()
        cursorObj.close()