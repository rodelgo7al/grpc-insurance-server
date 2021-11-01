--    Copyright 2021 Alberto Rodelgo

--    Licensed under the Apache License, Version 2.0 (the "License");
--    you may not use this file except in compliance with the License.
--    You may obtain a copy of the License at

--        http://www.apache.org/licenses/LICENSE-2.0

--    Unless required by applicable law or agreed to in writing, software
--    distributed under the License is distributed on an "AS IS" BASIS,
--    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--    See the License for the specific language governing permissions and
--    limitations under the License.

CREATE TABLE "agents" (
	"id"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE "agents_policies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"agent_id"	INTEGER NOT NULL,
	"policy_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("agent_id") REFERENCES "agents"("id") on update cascade on delete cascade,
	FOREIGN KEY("policy_id") REFERENCES "policies"("id") on update cascade on delete cascade
)

CREATE TABLE "agents_users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"agent_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("id") on update cascade on delete cascade,
	FOREIGN KEY("agent_id") REFERENCES "agents"("id") on update cascade on delete cascade
)

CREATE TABLE "policies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"mobile_number"	TEXT NOT NULL CHECK(length("mobile_number") == 10 AND "mobile_number" LIKE '_%' AND "mobile_number" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
	"premium"	INTEGER NOT NULL,
	"type"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("mobile_number","premium","type") ON CONFLICT IGNORE
)

CREATE TABLE "users" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"mobile_number"	TEXT NOT NULL CHECK(length("mobile_number") == 10 AND "mobile_number" LIKE '_%' AND "mobile_number" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]') UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("name","mobile_number") ON CONFLICT IGNORE
)

CREATE TABLE sqlite_sequence(name,seq)
