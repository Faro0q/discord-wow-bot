import os
import discord
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_dict = {'farooqq':'0', 'zuruhgar':'0', 'btracks':'0', 'meatsmoothie':'0', 'setralanat':'0', 'rhcisbae':'0'}

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
        updated_dict = namespace_profile_us(access_token, "", 'equipped_item_level')

        title="List of Users Item Level: Thrall"
        color=discord.Color.from_rgb(68,128,168)
        description="This will display your current item level"
        embed_key="Name"
        embed_value="ilvl"
        embed = get_embed(title, color, description, embed_key, embed_value, updated_dict)
        await message.channel.send(embed=embed)
    
    # arena rating
    if message.content.startswith('!arena'):
        access_token = create_access_token(os.getenv('client_id'), os.getenv('client_secret'))
        updated_dict = namespace_profile_us(access_token, "/pvp-bracket/2v2", 'rating')
        
        title="List of Users 2v2 Arena Rating: Thrall"
        color=discord.Color.from_rgb(176, 9, 9)
        description="This will display your arena rating"
        embed_key="Name"
        embed_value="Rating"
        embed = get_embed(title, color, description, embed_key, embed_value, updated_dict)
        await message.channel.send(embed=embed)


def namespace_profile_us(wow_token, arena_url, json_var):
    for user in user_dict:
        url = f'https://us.api.blizzard.com/profile/wow/character/thrall/{user}{arena_url}?namespace=profile-us&locale=en_US&access_token={wow_token}'
        try:
            response = requests.get(url)
            users_item_lvl = response.json()[json_var]
            user_dict[user] = str(users_item_lvl)
        except KeyError as e:
            user_dict[user] = str("0")
            print('Json not found:', e)

    # sort the dictionary by value in descending order
    sorted_dict = sorted(user_dict, key=user_dict.get, reverse=True)
    # create a new dictionary using the sorted keys
    new_dict = dict((key, user_dict[key]) for key in sorted_dict)
    return new_dict

def get_embed(title, color, description, embed_key, embed_value, updated_dict):
    embed=discord.Embed(
            title=title,
            color=color,
            description=description
        )
    embed.timestamp = datetime.datetime.now()
    embed.add_field(name=embed_key, value='\n'.join(updated_dict), inline="True")
    embed.add_field(name=embed_value, value='\n'.join(updated_dict.values()), inline="True")
    return embed

def create_access_token(client_id, client_secret, region = 'us'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    json_response = response.json()
    return json_response['access_token']


client.run(os.environ["token"])