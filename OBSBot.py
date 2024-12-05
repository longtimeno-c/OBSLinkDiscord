import discord
from obswebsocket import obsws, requests
import asyncio
import requests as http_requests  # For checking URL availability

# Configuration
discord_bot_token = 'YOUR_DISCORD_BOT_TOKEN'
channel_id = YOUR_CHANNEL_ID
obs_host = "localhost"
obs_port = 4444
obs_password = "your_obs_password"

client = discord.Client()
user_scenes = {}  # Dictionary to keep track of user scenes

def create_obs_connection():
    ws = obsws(obs_host, obs_port, obs_password)
    ws.connect()
    return ws

def scene_exists(ws, scene_name):
    """ Check if a scene exists in OBS """
    scenes = ws.call(requests.GetSceneList())
    for scene in scenes.getScenes():
        if scene['name'] == scene_name:
            return True
    return False

def delete_scene(ws, scene_name):
    """ Delete a scene in OBS """
    if scene_exists(ws, scene_name):
        ws.call(requests.RemoveScene(scene_name))

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="Waiting for phone cam links"))

@client.event
async def on_message(message):
    if message.channel.id != channel_id or message.author == client.user:
        return

    urls = [word for word in message.content.split() if word.startswith('http')]
    if not urls:
        return

    nickname = message.author.nick or message.author.name  # Use nickname if available, otherwise username
    scene_name = f"{nickname}phonecam"
    
    ws = create_obs_connection()

    try:
        if scene_name in user_scenes and user_scenes[scene_name] != message.author.id:
            delete_scene(ws, scene_name)  # Delete old scene if different user

        user_scenes[scene_name] = message.author.id  # Update scene ownership

        for url in urls:
            if is_url_active(url):
                if not scene_exists(ws, scene_name):
                    ws.call(requests.CreateScene(scene_name))
                ws.call(requests.SetSourceSettings("Browser Source", {"url": url, "width": 1920, "height": 1080}, scene_name=scene_name))
                print(f"Created/Updated scene {scene_name} with URL: {url}")
                await asyncio.sleep(20)
                if scene_exists(ws, scene_name):
                    ws.call(requests.SetCurrentScene(scene_name))
                else:
                    print(f"Scene {scene_name} was deleted manually. Cannot switch to it.")
            else:
                print(f"URL is inactive: {url}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ws.disconnect()

def is_url_active(url):
    """ Check if the URL returns a 200 OK status """
    try:
        response = http_requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except http_requests.RequestException:
        return False

client.run(discord_bot_token)