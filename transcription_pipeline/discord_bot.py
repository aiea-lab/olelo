"""
reference - https://builtin.com/software-engineering-perspectives/discord-bot-python
"""




import logging
import sys, os
import torch
from transformers import WhisperFeatureExtractor
import numpy as np
import os
import random
import discord
import nltk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio
import spacy
nlp = spacy.load("en_core_web_sm")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.guild_messages = True
intents.message_content = True

import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

print("File loaded. __name__ =", __name__)

bot = discord.Client(intents = intents)

app = FastAPI(title="sample")

logger = logging.getLogger("uvicorn.error")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # This ensures the traceback is still printed to your terminal console
    logger.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})


def split_text(summary):
    print(" at aplit")
    doc = nlp(summary)
    print(" at aplis")

    
    chunks = []
    chunks.append("----------------------------------------------------")


    max_len = 1800
    summ_str = ""

    for s in doc.sents:
        if len(s.text) + len(summ_str) <= max_len:
            summ_str += s.text
        else:
            chunks.append(summ_str)
            summ_str = s.text 
        
    chunks.append("----------------------------------------------------")
    return chunks

@bot.event
async def on_ready():
	# CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
	guild_count = 0

	# LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
	for guild in bot.guilds:
		# PRINT THE SERVER'S ID AND NAME.
		print(f"- {guild.id} (name: {guild.name})")

		# INCREMENTS THE GUILD COUNTER.
		guild_count = guild_count + 1

	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
	print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.



@bot.event
async def on_message(message):
	# CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO".
    
    if message.content == "hello":
		# SENDS BACK A MESSAGE TO THE CHANNEL.

        await send_transcripts(message)


async def send_transcripts(message):
	# CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO".
     
    channel = bot.get_channel(1506427721608073248)
    print("the chunky sending to chunks")
    chunks = split_text(message)
    
    for i in chunks:
        print("sending", i)
        await channel.send(i)


async def run_discord_bot():
    print('STARTING DISCORD BOT')
    await bot.start(DISCORD_TOKEN)
		
async def run_api():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        reload=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot():
    print("we are now running the bot")
    await bot.start(DISCORD_TOKEN)


async def main():
    print('RUNNING MAIN')
    await asyncio.gather(
        run_bot(),
        run_api(),
        
    )


if __name__ == "discord_bot":
    print("Running now")
    asyncio.run(main())
