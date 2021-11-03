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

from app.db_manager import DBManager
import settings

import asyncio
import logging

import settings
import sys
import traceback

from app.async_insurer_server import GRPCServer

def main():
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    try:
        db_manager = DBManager(settings.DB_FILE)
    except:
        logging.info("An exception ocurred. Ending application...")
        loop.close()
        raise

    try:
        db_manager.create_agent(settings.AGENT_ID)
        server = GRPCServer(db_manager)
        group = asyncio.gather(server.start())
    except:
        logging.info("An exception ocurred. Ending application6...") 
        db_manager.close()
        loop.close()
        raise

    try:
        loop.run_until_complete(group)
    except KeyboardInterrupt:
        pass
    except Exception as er:
        logging.info("An exception ocurred. Ending application...")
        logging.error(traceback.format_exc())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(*server._cleanup_coroutines)
        loop.close()
        db_manager.close()
        
        sys.exit()

if __name__ == "__main__":
    main()