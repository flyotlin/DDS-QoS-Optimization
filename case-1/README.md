# Case 1
## How to Run
You need to prepare fastdds environment in advance.
- `$ cd case-1/src`
- `$ fastddsgen -python SimpleString.idl`
- `$ cmake .`
- `$ make`
- `$ python3 subscriber.py <configName> <totalMsgs> <sendingRate> <topicName>`
- `$ python3 publisher.py <configName> <totalMsgs> <topicName>`

## Publisher & Subscriber
### Publisher
- arguments
  - `configName`: yaml config name (e.g., OMG-Def)
  - `totalMsgs`: total messages (samples) sent
  - `sendingRate`: publish rate (messages/sec)
  - `topicName`: topic name to which publishes
### Subscriber
- arguments
  - `configName`: yaml config name (e.g., OMG-Def)
  - `totalMsgs`: total messages (samples) sent
  - `topicName`: topic name to which publishes
