import asyncio
import websockets
import json
import logging
import time
import random

COOLDOWN_DURATION = 300  # 5 minutes in seconds
REMINDER_INTERVAL = 3600  # 1 hour in seconds
# Set up logging
logging.basicConfig(level=logging.DEBUG)

# {websocket: {username, last_tag_time, failed_tag_time, total_tagged_time, is_on_cooldown}}
connected_users = {}


async def handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "register":
                username = data["username"]
                connected_users[websocket] = {
                    "username": username,
                    "last_tag_time": None,
                    "failed_tag_time": None,
                    "total_tagged_time": 0,
                    "is_on_cooldown": False
                }
                await broadcast_user_list()

            elif data["type"] == "tag":
                sender = connected_users[websocket]["username"]
                target_username = data["target"]

                # Check if sender is on cooldown
                if connected_users[websocket]["is_on_cooldown"]:
                    await websocket.send(json.dumps({"type": "notification", "message": "You are on cooldown and can't tag right now."}))
                    continue

                # Determine success or failure (luck-based)
                if random.random() < 0.5:  # 50% success rate
                    await successful_tag(sender, target_username)
                else:
                    await failed_tag(websocket, sender, target_username)

    except websockets.exceptions.ConnectionClosed:
        if websocket in connected_users:
            del connected_users[websocket]
            await broadcast_user_list()


async def successful_tag(sender, target_username):
    now = time.time()
    target_ws = None

    # Find the target user and record tag
    for ws, user_data in connected_users.items():
        if user_data["username"] == target_username:
            target_ws = ws
            user_data["last_tag_time"] = now
            user_data["total_tagged_time"] += 1  # Increment total tagged time
            break

    # Notify the target
    if target_ws:
        await target_ws.send(json.dumps({"type": "notification", "message": f"{sender} successfully tagged you!"}))

    # Notify the sender
    for ws, user_data in connected_users.items():
        if user_data["username"] == sender:
            await ws.send(json.dumps({"type": "notification", "message": f"You successfully tagged {target_username}!"}))


async def failed_tag(sender_ws, sender, target_username):
    now = time.time()

    # Put sender on cooldown
    connected_users[sender_ws]["failed_tag_time"] = now
    connected_users[sender_ws]["is_on_cooldown"] = True

    # Notify sender
    await sender_ws.send(json.dumps({"type": "notification", "message": f"Failed to tag {target_username}. You are on cooldown for 5 minutes."}))

    # Notify target
    for ws, user_data in connected_users.items():
        if user_data["username"] == target_username:
            await ws.send(json.dumps({"type": "notification", "message": f"{sender} tried to tag you but failed!"}))

    # Start cooldown timer
    asyncio.create_task(remove_cooldown(sender_ws))


async def remove_cooldown(ws):
    await asyncio.sleep(COOLDOWN_DURATION)
    if ws in connected_users:
        connected_users[ws]["is_on_cooldown"] = False


async def send_reminders():
    while True:
        for ws, user_data in connected_users.items():
            if user_data["last_tag_time"]:
                await ws.send(json.dumps({"type": "notification", "message": "Reminder: It's your turn to tag!"}))
        await asyncio.sleep(REMINDER_INTERVAL)


async def broadcast_user_list():
    sorted_users = sorted(
        connected_users.values(),
        key=lambda user: user["total_tagged_time"],
        reverse=True
    )
    usernames = [user["username"] for user in sorted_users]
    for ws in connected_users:
        await ws.send(json.dumps({"type": "userListUpdate", "users": usernames}))


async def send_notification(target_username, message):
    # Find the WebSocket connection of the target user
    for ws, username in connected_users.items():
        if username == target_username:
            await ws.send(json.dumps({"type": "notification", "message": message}))
            logging.debug(f"Notification sent to {target_username}: {message}")
            break

start_server = websockets.serve(handler, "127.0.0.1", 8080)


asyncio.get_event_loop().run_until_complete(start_server)
logging.debug("WebSocket server started")
asyncio.get_event_loop().run_forever()
asyncio.create_task(send_reminders())
