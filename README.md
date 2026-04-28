# OBSLinkDiscord

A Discord bot that watches a specific channel and automatically creates a new OBS scene containing a Browser Source for any URL posted there. After a short delay the bot switches OBS to that scene — great for quickly pulling phone-camera streams or other web sources into a live production.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Building a Standalone Executable (.exe)](#building-a-standalone-executable-exe)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)

---

## Features

- Monitors a single Discord channel for messages that contain URLs.
- Automatically creates a uniquely named OBS scene per Discord user (`<nickname>phonecam`).
- Adds a 1920×1080 Browser Source pointing to the posted URL.
- Switches OBS to the new scene after a configurable delay (default 20 s).
- Cleans up old scenes when the same user posts a new link.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.9 or newer |
| OBS Studio | 28 or newer |
| obs-websocket plug-in | 5.x (bundled with OBS 28+) |

Python package dependencies are listed in [`requirements.txt`](requirements.txt):

```
discord.py>=2.3.2
obs-websocket-py>=1.0
requests>=2.31.0
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/longtimeno-c/OBSLinkDiscord.git
cd OBSLinkDiscord
```

### 2. Create and activate a virtual environment (recommended)

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Open `OBSBot.py` and edit the values at the top of the file:

```python
# Your Discord bot token (from https://discord.com/developers/applications)
discord_bot_token = 'YOUR_DISCORD_BOT_TOKEN'

# The numeric ID of the Discord channel to monitor
# (Right-click the channel → Copy Channel ID — requires Developer Mode)
channel_id = YOUR_CHANNEL_ID

# OBS WebSocket settings
obs_host = "localhost"   # Change if OBS runs on a different machine
obs_port = 4444          # Default OBS WebSocket port
obs_password = "your_obs_password"  # Set in OBS → Tools → WebSocket Server Settings
```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Navigate to **Bot** → **Add Bot**.
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**.
4. Copy the **token** and paste it into `discord_bot_token`.
5. Under **OAuth2 → URL Generator**, select the `bot` scope and at minimum the `Read Messages/View Channels` and `Read Message History` permissions.
6. Open the generated URL, select your server, and authorise the bot.

### OBS WebSocket Setup

1. In OBS, go to **Tools → WebSocket Server Settings**.
2. Enable the server, set a password, and note the port (default `4444`).
3. Enter these values in `OBSBot.py`.

---

## Running the Bot

Make sure OBS is open and the WebSocket server is running, then:

```bash
python OBSBot.py
```

The bot will print `Logged in as <BotName>` once it has connected to Discord.  
Post any `http://…` or `https://…` URL in the configured channel to trigger it.

---

## Building a Standalone Executable (.exe)

You can package the bot into a single Windows executable so it can be run without installing Python.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the executable

```bash
pyinstaller --onefile --name OBSLinkDiscord OBSBot.py
```

| Flag | Meaning |
|---|---|
| `--onefile` | Bundle everything into a single `.exe` |
| `--name OBSLinkDiscord` | Name of the output file |

### 3. Locate the output

After the build completes, the executable is in the `dist/` folder:

```
dist/
└── OBSLinkDiscord.exe
```

### 4. Run the executable

Double-click `OBSLinkDiscord.exe` or launch it from a terminal:

```bash
dist\OBSLinkDiscord.exe
```

> **Note:** Before distributing the executable, make sure you have updated the configuration values (`discord_bot_token`, `channel_id`, `obs_password`) inside `OBSBot.py`. The compiled binary contains the values that were present at build time.

---

## How It Works

1. **Message received** – the bot listens for any message in the configured channel.
2. **URL detection** – any word starting with `http` is treated as a URL.
3. **URL validation** – the bot sends a `HEAD` request to confirm the URL returns HTTP 200 before proceeding.
4. **Scene management** – a scene named `<nickname>phonecam` is created in OBS (or reused if it already exists). If a different user previously owned that scene name it is deleted first.
5. **Browser Source** – a `browser_source` input at 1920×1080 is added to the scene pointing to the URL.
6. **Switch delay** – the bot waits 20 seconds (configurable via `asyncio.sleep`) then switches OBS to the new scene.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `discord.errors.LoginFailure` | Check that your bot token is correct and has not been regenerated. |
| `ConnectionRefusedError` (OBS) | Ensure OBS is running and the WebSocket server is enabled with the correct port and password. |
| Scene not switching | The scene may have been deleted manually during the 20 s delay. Check the console for a warning message. |
| URL marked as inactive | The URL returned a non-200 status. Verify the stream/page is publicly accessible. |
| `ModuleNotFoundError` after building `.exe` | Re-run PyInstaller inside the virtual environment where all packages are installed. |
