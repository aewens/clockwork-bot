#!/usr/bin/env python3

# Built-in packages
import re
import sys
import json
import traceback
import threading
from random import randint 
from time import time, sleep
from datetime import datetime
from operator import itemgetter

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

def get_news(bot, client):
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
    topic_list = list()
    for topic in update_topics:
        topic_timestamp = get_timestamp(topic[created])
        time_since = now - topic_timestamp + adjust_timezone

        topic_id = topic["id"]
        slug = topic["slug"]
        update_topic = client.topic(topic_id=topic_id, slug=slug)
        all_posts = update_topic["post_stream"]["posts"]
        first_post = all_posts[0]
        post_username = first_post["username"]
        if post_username in watch:
            topic_list.append([time_since, first_post]) 
    
    most_recent = sorted(topic_list, key=itemgetter(0))[0][1]

    message = re.sub(r"<(.*?)>", "", first_post["cooked"])
    post_number = first_post["post_number"]
    link_tuple = (discourse_site, slug, topic_id, post_number)
    link = "%st/%s/%s/%s" % link_tuple
    if len(message) > 1500:
        message = "%s..." % message[:1500]
    post_message = "%s: %s [%s]" % (post_username, message, link)
    return post_message

def get_news_channel(bot):
    channels = bot.get_all_channels()
    return [channel for channel in channels if str(channel) == "news"][0]
                
@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    print("="*max(len(bot.user.name), len(bot.user.id)))

@bot.event
async def on_message(message):
    if message.content.startswith("!test"):
        await bot.send_message(message.channel, "Test successful!")
    elif message.content.startswith("!random"):
        await bot.send_message(message.channel, "%s" % randint(0,100))
    elif message.content.startswith("!news"):
        roles = [str(role) for role in message.author.roles]
        if str(message.channel) == "news":
            if "Moderator" in roles or "News Reporter" in roles:
                news_message = get_news(bot, discourse_client)
                await bot.send_message(message.channel, news_message)
        

bot.run(discord_token)
