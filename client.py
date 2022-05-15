import asyncio
import websockets
import json
async def enter():
  # while True:
    try:
        async with websockets.connect('ws://39.99.249.45:8099/send') as websocket:
            content={"action": 'audience_enter',"content": {"user_id": '0x0df234'}}
            content=json.dumps(content)
            await websocket.send(content)
            # recv_msg = await websocket.recv()
            # print(recv_msg)
    except websockets.exceptions.ConnectionClosedError as e:
        print("connection closed error")
    except Exception as e:
        print(e)

async def vote():
  # while True:
    try:
        async with websockets.connect('ws://39.99.249.45:8099/send') as websocket:
            content={"action": 'vote',"content": {"name": 'Biden'}}
            content=json.dumps(content)
            await websocket.send(content)
            # recv_msg = await websocket.recv()
            # print(recv_msg)
    except websockets.exceptions.ConnectionClosedError as e:
        print("connection closed error")
    except Exception as e:
        print(e)



async def send():
  # while True:
    try:
        async with websockets.connect('ws://39.99.249.45:8099/send') as websocket:
            content={"action": 'send_message',"content": {"user_id": '0x0df234',"timestamp":"2749458","message":"Fine!How are you guys?"}}
            # content={"action": 'vote',"content": {"name": 'Biden'}}
            # content={"action":"refresh"}
            # content={"action": 'audience_enter',"content": {"user_id": '0x0df234'}}
            content=json.dumps(content)
            await websocket.send(content)
            # websocket.close()
            # recv_msg = await websocket.recv()
            # print(recv_msg)
    except websockets.exceptions.ConnectionClosedError as e:
        print("connection closed error")
    except Exception as e:
        print(e)

async def message():
  while True:
    try:
        async with websockets.connect('ws://127.0.0.1:8099/0x0df2343/message') as websocket:
            # content={"action": 'send_message',"content": {"user_id": '0x0df234',"timestamp":"2749458","message":"how are you?"}}
            # await websocket.send(content)
            recv_msg = await websocket.recv()
            print(recv_msg)
    except websockets.exceptions.ConnectionClosedError as e:
        print("connection closed error")
    except Exception as e:
        print(e)

# async def main_logic():
#     async with websockets.connect('ws://10.10.6.91:5678') as websocket:
#         await auth_system(websocket)
# 
#         await send_msg(websocket)


# loop=asyncio.get_event_loop()
# tasks=loop.create_task([message(),enter(),vote(),send()])
# rst=loop.run_until_complete(tasks)
# run_until_complete(message())
# asyncio.get_event_loop().run_until_complete(vote())
# time.sleep(2)
asyncio.get_event_loop().run_until_complete(message())
# asyncio.get_event_loop().run_until_complete(send())
# asyncio.get_event_loop().run_until_complete(message())
