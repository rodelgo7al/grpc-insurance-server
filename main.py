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

from db_manager import DBManager
import settings

import asyncio
import logging

import settings
import sys

from async_insurer_server import Server

def main():
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()

    db_manager = DBManager(settings.DB_FILE)
    db_manager.create_agent(settings.AGENT_ID)

    server = Server(db_manager)
    asyncio.ensure_future(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        db_manager.close()
        loop.run_until_complete(server.server_graceful_shutdown())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(*server._cleanup_coroutines)
        loop.close()
        
        sys.exit()

if __name__ == "__main__":
    main()