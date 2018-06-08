#!/usr/bin/env python3

# Built-in packages
import re
import sys
import json
import traceback
import threading
from time import time, sleep
from datetime import datetime

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
    
discourse_site = discourse_config.get("site", None)
discourse_username = discourse_config.get("username", None)
discourse_api_key = discourse_config.get("api_key", None)

if discourse_site is None:
    print("Error: No discourse site provided")
    sys.exit(1)
    
if discourse_username is None:
    print("Error: No discourse username provided")
    sys.exit(1)
    
if discourse_api_key is None:
    print("Error: No discourse api_key provided")
    sys.exit(1)

bot = discord.Client()
discord_token = discord_config.get("token", None)

if discord_config is None:
    print("Error: No discord token provided")
    sys.exit(1)
    
discourse_client = DiscourseClient(
    discourse_site,
    api_username=discourse_username,
    api_key=discourse_api_key
)

async def every(delay, task, loop, **kwargs):
    next_time = loop.time() + delay
    while True:
        await asyncio.sleep(max(0, next_time - loop.time()))
        try:
            await task(**kwargs)
        except Exception:
            traceback.print_exc()
        next_time = loop.time() + delay

async def discourse_daemon(bot, client, wait):
    watch = ["yong", "hal"]
    latest = "last_posted_at"
    created = "created_at"
    # Adjust this according to where your server is located
    adjust_timezone = 5 * 60 * 60
    now = datetime.now().timestamp()
    update_id, update_slug = 257, "gameshell-updates"
    date_format = lambda _: datetime.strptime(_, "%Y-%m-%dT%H:%M:%S.%fZ")
    get_timestamp = lambda _: date_format(_).timestamp()
    
    topics = client.latest_topics()["topic_list"]["topics"]
    update_topics = [topic for topic in topics if "update" in topic["tags"]]
    for topic in update_topics:
        topic_timestamp = get_timestamp(topic[created])
        time_since = now - topic_timestamp + adjust_timezone
        if time_since <= wait:
            topic_id = topic["id"]
            slug = topic["slug"]
            update_topic = client.topic(topic_id=topic_id, slug=slug)
            all_posts = update_topic["post_stream"]["posts"]
            first_post = all_posts[0]
            post_username = first_post["username"]
            if post_username in watch:
                message = re.sub(r"<(.*?)>", "", first_post["cooked"])
                post_number = first_post["post_number"]
                link_tuple = (discourse_site, slug, topic_id, post_number)
                link = "%st/%s/%s/%s" % link_tuple
                post_message = "%s: %s [%s]" % (post_username, message, link)
                print(int(now), post_message)
                await bot.send_message(bot.news_channel, post_message)
                
    # if time_since <= wait and post_username in watch:

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    print("="*max(len(bot.user.name), len(bot.user.id)))
    for channel in bot.get_all_channels():
        if str(channel) == "news":
            setattr(bot, "news_channel", channel)
    
    minutes = lambda m: m * 60
    delay = minutes(1)
    
    loop = asyncio.get_event_loop()
    # DEBUG
    asyncio.ensure_future(discourse_daemon(bot, discourse_client, delay))
    # asyncio.ensure_future(every(
    #     delay, discourse_daemon, loop, 
    #     bot=bot, client=discourse_client, wait=delay
    # ))

@bot.event
async def on_message(message):
    if message.content.startswith("!test"):
        await bot.send_message(message.channel, "Test successful!")
    # More commands go here

bot.run(discord_token)
