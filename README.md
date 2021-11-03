# GRPC Insurance Server in Python

This code implements a simple gRPC server that retrieves policyholders and insurance policies from a REST API, stores the data using sqlite, and provides endpoints to query this data.

## Installation
This code has been developed in Python 3.7. The following packages are needed to execute this project. 
```
pip install grpcio
pip install grpcio-tools
pip install aiohttp
```

## Endpoints

A small Rest API Server has been implemented that provides data with the endpoints listed below.

| Verb   | Route                    | Action             |
|   ---: | :---                     | :---               |
| `GET`  | `/users/:agentId`                 | Get users for a given Insurance Agent              |
| `GET`  | `/policies/:agentId` | Get policies for a given Insurance Agent |


## Database
The data received from the REST API is stored and queried in this file, defined by the following tables:

- Agents (id)
- Policies (id, mobile_number, premium, type)
- Users (id, name, mobile_number)
- Agents_users (id, agent_id, user_id)
- Agents_policies (id, agent_id, policy_id)

## Launch
To execute this project is neccessary to run the REST Api and the gRPC Server.

### Server
Run
```
python app/rest_api_server.py
python main_server.py
```
Or
```
./execute_app.sh
```
### Client
To execute the GRPC Client, run the command below
```
python main_client.py
```

## Test
There is a shell script that executes some unit tests for the application:

```
./tests/execute_tests.sh
```

## References

https://grpc.io/docs/languages/python/basics/

https://docs.aiohttp.org/en/stable/




