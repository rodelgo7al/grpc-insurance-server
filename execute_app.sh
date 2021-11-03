#!/bin/bash

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


killbg() {
        for p in "${pids[@]}" ; do
                kill "$p";
        done
}
# Kill all processes when EXIT
trap killbg EXIT
pids=()
# Run REST API
python app/rest_api_server.py &
sleep 1
pids+=($!)
# Run GRPC Server 
# Modify flags as needed: (flags: -ams-api-url -schedule_period)
python main_server.py "http://localhost:8080" 0 &
pids+=($!)

sleep 5
read -p $'Press any key to exit...\n===========\n'

echo "Exit" 