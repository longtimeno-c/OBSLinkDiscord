import discord
from obswebsocket import obsws, requests

# Configuration
discord_bot_token = 'YOUR_DISCORD_BOT_TOKEN'
channel_id = YOUR_CHANNEL_ID  # The specific channel ID to listen to
obs_host = "localhost"
obs_port = 4444
obs_password = "your_obs_password"

client = discord.Client()

def create_obs_connection():
    ws = obsws(obs_host, obs_port, obs_password)
    ws.connect()
    return ws

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Set the bot's status
    await client.change_presence(activity=discord.Game(name="Waiting for phone cam links"))

@client.event
async def on_message(message):
    # Check if the message is from the specific channel
    if message.channel.id != channel_id or message.author == client.user:
        return

    # Check if the message contains a URL
    words = message.content.split()
    urls = [word for word in words if word.startswith('http')]
    if len(urls) == 0:
        return

    # Connect to OBS WebSocket
    ws = create_obs_connection()
    
    try:
        for url in urls:
            # Create or update scene with browser source
            scene_name = "Discord Link Scene"
            ws.call(requests.SetCurrentScene(scene_name))
            ws.call(requests.SetSourceSettings("Browser Source", {"url": url, "width": 1920, "height": 1080}))
            print(f"Updated scene with URL: {url}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ws.disconnect()

client.run(discord_bot_token)