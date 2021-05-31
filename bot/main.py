import discord
import requests
import json
import random
import os
from tinydb import TinyDB, Query

client = discord.Client()
token = os.getenv('DISCORD_BOT_TOKEN')

encourageDB = TinyDB("encouragements.json")
query = Query()
sad_words = ["sadge", ":sadge:"]
starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person / bot!"
]

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def updateEncouragements(encouragingMessage):
    encourageDB.insert({'encouragement': encouragingMessage})
    
def deleteEncouragements(index):
    messageExists = encourageDB.contains(doc_id=index)
    if messageExists:
        encourageDB.remove(doc_ids=[index])

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg = message.content
    encourageExists = encourageDB.search(query.encouragement.exists())

    if msg.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    options = starter_encouragements
    if encourageExists:
        for item in encourageDB:
            options.append(item['encouragement'])

    if any(word in msg for word in sad_words):
        await message.channel.send(random.choice(options))

    if msg.startswith('$new'):
        encouragingMessage = msg.split('$new ',1)[1]
        updateEncouragements(encouragingMessage)
        await message.channel.send('New encouraging message added.')
    
    if msg.startswith('$del'):
        if encourageExists:
            index = int(msg.split('$del ',1)[1])
            deleteEncouragements(index)
            encouragements = []
            for item in encourageDB:
                encouragements.append(item['encouragement'])
            embedVar = discord.Embed(title='Encouragement List', description='')
            embedVar.add_field(name='Here are the remaining user-submitted encouragements:', value='\n'.join(encouragements))
            await message.channel.send(embed=embedVar)

    if msg.startswith('$display'):
        encouragements = []
        for item in encourageDB:
            encouragements.append(item['encouragement'])
        embedVar = discord.Embed(title='Encouragement List', description='')
        embedVar.add_field(name='Here are the remaining user-submitted encouragements:', value='\n'.join(encouragements))
        await message.channel.send(embed=embedVar)
    
client.run(token)