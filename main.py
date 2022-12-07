import os
import discord
import requests
import datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_dict = {'farooqq':'0', 'zuruhgar':'0', 'btracks':'0'}

@client.event
async def on_ready():
    print('Bot is ready!')
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # display item level for a user
    if message.content.startswith('!itemlevel'):
        access_token = create_access_token(os.getenv('client_id'), os.getenv('client_secret'))
        updated_dict = get_item_level(access_token)
        embed=discord.Embed(
            title="List of Users Item Level: Thrall",
            color=discord.Color.from_rgb(68,128,168),
            description="This will display your current item level"
        )
        embed.timestamp = datetime.datetime.now()
        embed.add_field(name="Name", value='\n'.join(updated_dict), inline="True")
        embed.add_field(name="ilvl", value='\n'.join(updated_dict.values()), inline="True")
        await message.channel.send(embed=embed)
    
    # arena rating
    if message.content.startswith('!arena'):
        access_token = create_access_token(os.getenv('client_id'), os.getenv('client_secret'))
        updated_dict = get_arena_rating(access_token)
        # await message.channel.send(ss)
        embed=discord.Embed(
            title="List of Users 2v2 Arena Rating: Thrall",
            color=discord.Color.from_rgb(176, 9, 9),
            description="This will display your arena rating"
        )
        embed.timestamp = datetime.datetime.now()
        embed.add_field(name="Name", value='\n'.join(updated_dict), inline="True")
        embed.add_field(name="Rating", value='\n'.join(updated_dict.values()), inline="True")
        await message.channel.send(embed=embed)



# Iterate through a list of all the players and display their item level
def get_item_level(wow_token):
    for user in user_dict:
        url = f'https://us.api.blizzard.com/profile/wow/character/thrall/{user}?namespace=profile-us&locale=en_US&access_token={wow_token}'
        try:
            response = requests.get(url)
            users_item_lvl = response.json()['equipped_item_level']
            user_dict[user] = str(users_item_lvl)
        except requests.exceptions.RequestException as e:
            print('Error:', e)

    # sort the dictionary by value in descending order
    sorted_dict = sorted(user_dict, key=user_dict.get, reverse=True)

    # create a new dictionary using the sorted keys
    new_dict = dict((key, user_dict[key]) for key in sorted_dict)
    
    return new_dict

def get_arena_rating(wow_token):
    for user in user_dict:
        url_2v2 = f'https://us.api.blizzard.com/profile/wow/character/thrall/{user}/pvp-bracket/2v2?namespace=profile-us&locale=en_US&access_token={wow_token}'
        try:
            response = requests.get(url_2v2)
            users_rating = response.json()['rating']
            user_dict[user] = str(users_rating)
        except KeyError as e:
            user_dict[user] = str("0")
            print('Error:', e)
    
    # sort the dictionary by value in descending order
    sorted_dict = sorted(user_dict, key=user_dict.get, reverse=True)

    # create a new dictionary using the sorted keys
    new_dict = dict((key, user_dict[key]) for key in sorted_dict)

    return new_dict


def create_access_token(client_id, client_secret, region = 'us'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    json_response = response.json()
    return json_response['access_token']


client.run(os.getenv('token'))
