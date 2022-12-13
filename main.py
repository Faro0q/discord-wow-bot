import os
import discord
import requests
import datetime
import aiohttp
import asyncio
import re
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

EVENTS = []
COUNT = 1
user_dict = {user: {'ilvl': 0, '2v2': 0, '3v3': 0} for user in ['farooqq', 'zuruhgar', 'btracks', 'meatsmoothie', 'setralanat', 'rhcisbae', 'takisbae', 'genisonamue', 'farooqin', 'heracleez']}

@client.event
async def on_ready():
    print('Bot is ready!')
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # display item level for a user
    if message.content.startswith('!itemlevel'):
        access_token = create_access_token(os.environ["client_id"], os.environ["client_secret"])
        # loop = asyncio.get_event_loop()
        updated_dict = await client.loop.create_task(namespace_profile_us(access_token, "", 'equipped_item_level', 'ilvl')) # run the coroutine in the event loop
        title="List of Users Item Level(PvE): Thrall"
        color=discord.Color.from_rgb(68,128,168)
        description="This will display your current item level"
        embed_value="ilvl"
        embed = get_embed(title, color, description, embed_value, updated_dict, 'ilvl')
        await message.channel.send(embed=embed)
    
    # arena rating
    if message.content.startswith('!arena'):
        access_token = create_access_token(os.getenv('client_id'), os.getenv('client_secret'))
        loop = asyncio.get_event_loop()
        updated_dict =await client.loop.create_task(namespace_profile_us(access_token, "/pvp-bracket/2v2", 'rating', '2v2'))
        title="List of Users 2v2 Arena Rating: Thrall"
        color=discord.Color.from_rgb(176, 9, 9)
        description="This will display 2v2 your arena rating"
        embed_value="Rating"
        embed = get_embed(title, color, description, embed_value, updated_dict, '2v2')
        await message.channel.send(embed=embed)

        loop = asyncio.get_event_loop()
        updated_dict = await client.loop.create_task(namespace_profile_us(access_token, "/pvp-bracket/3v3", 'rating', '3v3'))
        title="List of Users 3v3 Arena Rating: Thrall"
        color=discord.Color.from_rgb(176, 9, 176)
        description="This will display your 3v3 arena rating"
        embed = get_embed(title, color, description, embed_value, updated_dict, '3v3')
        await message.channel.send(embed=embed)

    # Events config
    if message.content.startswith('!event help'):
        await message.channel.send("To create an event, please use this format:\n `!create event CSGO 06/08 09:00 @csnerd`")
        await message.channel.send("To delete an event, please use this format:\n `!delete event 1`")

    if message.content.startswith('!events'):
        if(len(EVENTS) == 0):
            await message.channel.send("No events")
        else:
            # output = globalCount + 
            await message.channel.send('Events:\n')
            for x in EVENTS:
                await message.channel.send(str(x))

    if message.content.startswith('!create event'):
        userMessage = message.content.split(" ")
        wrongFormat = event_create_format_checker(userMessage)
        if(wrongFormat):
            await message.channel.send(wrongFormat)
        else:
            newEvent(userMessage, message.author)
            await message.channel.send("Event added! Type '!events' to list all the events")
    
    if message.content.startswith('!delete event'):
        userMessage = message.content.split(" ")
        wrongFormat = event_delete_format_checker(userMessage)
        if(wrongFormat):
            await message.channel.send(wrongFormat)
        else:
            event_num = int(userMessage[2]-1)
            deleted = EVENTS.pop(event_num)
            await message.channel.send(f"Event: {deleted} has been deleted.")
    


async def namespace_profile_us(wow_token, arena_url, json_var, dict_value):
    # iterate over the keys in the user_dict dictionary
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in user_dict:
            url = f'https://us.api.blizzard.com/profile/wow/character/thrall/{user}{arena_url}?namespace=profile-us&locale=en_US&access_token={wow_token}'
            # make an HTTP GET request to the URL
            task = asyncio.create_task(session.get(url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        for response in responses:
            json_data = await response.json()
            users_value = json_data.get(json_var, 0)
            if users_value == 0:
                continue
            if dict_value == "ilvl":
                user_name = json_data['name'].lower()
                if users_value < user_dict[user_name][dict_value]:
                    # skip updating the user_dict dictionary for this user
                    continue
                else:
                    user_dict[user_name][dict_value] = users_value
            else:
                user_name = json_data['character']['name'].lower()
                # update the value in the user_dict dictionary using the key_mapping dictionary
                user_dict[user_name][dict_value] = users_value

        # sort the dictionary by value in descending order
        sorted_dict = sorted(user_dict, key=lambda x: user_dict[x][dict_value], reverse=True)
        # create a new dictionary using the sorted keys
        new_dict = dict((key, user_dict[key]) for key in sorted_dict)
        return new_dict

def get_embed(title, color, description, embed_value, updated_dict, list_index):

    display_list = []
    embed_key="Name"
    for val in updated_dict:
        display_list.append(str(user_dict[val][list_index]))
    
    embed=discord.Embed(
            title=title,
            color=color,
            description=description
        )
    embed.timestamp = datetime.datetime.now()
    embed.add_field(name=embed_key, value='\n'.join(updated_dict), inline="True")
    embed.add_field(name=embed_value, value='\n'.join(display_list), inline="True")
    return embed

def event_delete_format_checker(msg):
    # !delete event 1

    if(len(msg) != 3):
        return "Incorrect format. Type 'event help' to see the correct format."
    
    event_num = msg[2]
    event_bool = event_num.isnumeric() # Check if its a num
    
    if not (event_bool):
        return "Provided event number is not numeric. Please provide values of 1, 2, 3, etc"
    if int(event_num) >= len(EVENTS):
        return "Event doesn't exist, make sure the event exist when typing '!events'" 
    else:
        return ""

def event_create_format_checker(msg):
    # Correct:
    # create event Valorant 03/02 09:00 @gello

    if(len(msg) < 5):
        return "Incorrect format. Type '!event help' to see the correct format."

    date = msg[3]
    time = msg[4]
    dateReg = re.search("^(0?[1-9]|1[012])/[1-2][0-9]|30|31|[0][1-9]$", date) # Check if date is valid
    timeReg = re.search("^(0[1-9]|1[0-9]|2[0123]):[0-5][0-9]$", time) # Check if time is valid
    
    if not (dateReg):
        return "Incorrect date format. Type '!event help' to see the correct format."
    if not (timeReg):
        return "Incorrect time format. Type '!event help' to see the correct format."
    else:
        return ""

def increment():
    global COUNT
    COUNT = COUNT+1

def newEvent(msg, author):
    # create csgo 9:00 @someone
    newEvent = ""
    for x in range(2, len(msg)):
        newEvent += msg[x] + " "
    
    event = "**" + newEvent.strip() + "**"
    author = "**" + str(author) + "**"
    EVENTS.append(str(COUNT) + ". " + event + " created by: " + author)
    increment()
    print(EVENTS)

def create_access_token(client_id, client_secret, region = 'us'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    json_response = response.json()
    return json_response['access_token']

client.run(os.environ["token"])