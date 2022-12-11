import os
import discord
import requests
import datetime
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_dict = {user: {'ilvl': 0, '2v2': 0, '3v3': 0} for user in ['farooqq', 'zuruhgar', 'btracks', 'meatsmoothie', 'setralanat', 'rhcisbae', 'takisbae']}

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

def create_access_token(client_id, client_secret, region = 'us'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    json_response = response.json()
    return json_response['access_token']

client.run(os.environ["token"])