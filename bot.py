#!/usr/bin/env python3

# Built-in packages
import sys
import json

# Third-party packages
import discord
import asyncio
from pydiscourse import DiscourseClient

try:
    config = json.loads(open("config.json", "r").read())
except ValueError as e:
    print("Error: Cannot load config.json: %s" % str(e))
    sys.exit(1)
    
discord_config = config.get("discord", None)
discourse_config = config.get("discourse", None)

if discord_config is None:
    print("Error: No discord settings provided")
    sys.exit(1)
    
if discourse_config is None:
    print("Error: No discourse settings provided")
    sys.exit(1)
    
client = discord.Client()
discord_token = discord_config.get("token", None)

if discord_config is None:
    print("Error: No discord token provided")
    sys.exit(1)

@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)
    print("="*max(len(client.user.name), len(client.user.id)))
    

@client.event
async def on_message(message):
    if message.content.startswith("!test"):
        await client.send_message(message.channel, "Test successful!")
    # More commands go here
    
client.run(discord_token)
