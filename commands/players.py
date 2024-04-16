import os
import discord
import requests
import xml.etree.ElementTree as ET
import json
import aiohttp
from discord.ext import commands
from discord import app_commands
from discord_webhook import DiscordWebhook
import re

with open('config.json') as config_file:
    config_data = json.load(config_file)
WEBHOOKURL = config_data['webhook']
OWNER = int(config_data['owner'])

XML_API_URL = 'https://edgegamers.gameme.com/api/serverinfo/104.128.58.156:27015/players'

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

image_links = {
    "avalanche": "https://i.imgur.com/ZfbV9vJ.png",
    "undertale": "https://i.imgur.com/CzzwLyF.png",
    "clouds": "https://i.imgur.com/qWntm6o.png",
    "minecraft": "https://i.imgur.com/3f27kd7.png",
    "quake": "https://i.imgur.com/lcPnokt.png",
    "spy": "https://i.imgur.com/PZUOLg8.png",
    "peanut": "https://i.imgur.com/t0bTOQv.png",
    "vipinthemix": "https://i.imgur.com/IB7E1d2.png",
    "kwejsi": "https://i.imgur.com/gza8kYA.png",
    "umbrella": "https://i.imgur.com/0HLqFuo.png",
    "unknown": "https://media.discordapp.net/attachments/1152808650436522045/1228862165105250325/video.gif?ex=662d9613&is=661b2113&hm=db8815275b4e99ae71163ce0640e050dd112579bb9adad4452455cc476f9a571&",
}



def scrape_xml():
    response = requests.get(XML_API_URL)
    if response.status_code == 200:
        root = ET.fromstring(response.content)

        # Find the <map> element
        mapinfo = root.find('.//server/map').text

        # Initialize empty lists for both teams

        ctlist = []
        tlist = []

        # Iterate through each player
        for player in root.findall('.//server/players/player'):
            player_name = player.find('name').text
            player_team = player.find('team').text

            # Depending on the team, append the player to the corresponding list
            if player_team == "CT":
                ctlist.append(player_name)
            elif player_team == "TERRORIST":
                tlist.append(player_name)
            # Optionally handle players without a team or with a different designation

        return mapinfo, tlist, ctlist
    else:
        return None, None, None  # Returning None values if fetching XML data fails




@client.hybrid_command(usage="/players")
async def players(ctx: discord.Member = None):
    current_time = discord.utils.utcnow() # this has to be an object, before I had: current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S') . but this didnt work
                                          # probably because of the ".strftime('%Y-%m-%d %H:%M:%S')" part which i think turned it into a string
    if ctx.guild is None:
        guild_name = "Private Messages"
    else:
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        guild_ownerid = ctx.guild.owner_id
        guild_owner = ctx.guild.owner

    if ctx.guild is None:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /players \nServer: ({guild_name})'
    else:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /players \nName: ({guild_name}) \nID: ({guild_id}) \nOwner: ({guild_owner}) \nID: ({guild_ownerid})'

    mapinfo = str(scrape_xml())
    image_data = ['avalanche', 'undertale', 'clouds', 'minecraft', 'quake', 'spy', 'peanut', 'vipinthemix', 'kwejsi', 'umbrella']
    map_match = re.search(r"'(.+?)'", mapinfo)
    if map_match:
        map_name = map_match.group(1)
    else:
        map_name = "unknown"  # Default to "unknown" if map name cannot be extracted

    split_info = map_name.split('_')

    # Debugging print statement
    print("Split info:", split_info)

    check = any(item in image_data for item in split_info)
    if check:
        if image_links != 'jail':
            try:
                image = image_links[split_info[1]]
                print("Selected Image:", image)  # Debugging print statement
            except IndexError:
                image = image_links["unknown"]
                print("Selected Image:", image)  # Debugging print statement
        else:
            try:
                image = image_links['umbrella']
            except IndexError:
                image = image_links["unknown"] 
    else:
        image = image_links["unknown"]
        print("Selected Image:", image)  # Debugging print statement



    mapinfo, tlist, ctlist = scrape_xml()
    if ctlist and tlist:
        midpoint1 = len(ctlist)//2
        midpoint2 = len(tlist)//3
    
        if len(ctlist) % 2 == 0:
            ctlist1 = ctlist[:midpoint1]
            ctlist2 = ctlist[midpoint1:]
        elif len(ctlist) % 2 != 0:
            ctlist1 = ctlist[:midpoint1+1]
            ctlist2 = ctlist[midpoint1+1:]

        if len(tlist) % 3 == 0:
            tlist1 = tlist[:midpoint2]
            tlist2 = tlist[midpoint2:midpoint2*2]
            tlist3 = tlist[midpoint2*2:]
        elif len(tlist) % 3 == 1:
            tlist1 = tlist[:midpoint2] + tlist[midpoint2*3::]
            tlist2 = tlist[midpoint2:midpoint2*2]
            tlist3 = tlist[midpoint2*2:midpoint2*3]
        elif len(tlist) % 3 == 2:
            tlist1 = tlist[:midpoint2] + tlist[midpoint2*3::2]
            tlist2 = tlist[midpoint2:midpoint2*2] + [tlist[midpoint2*3+1]]
            tlist3 = tlist[midpoint2*2:midpoint2*3]
    

        embed = discord.Embed(
            title=f"Click to connect\nMap: {mapinfo}",
            url="https://cs2browser.com/connect/104.128.58.156:27015",
            timestamp=current_time
        )

        embed.add_field(
            name="CT Players",
            value='\n'.join(map(str, ctlist1)),
            inline=True
            )
        embed.add_field(
            name="\u200b",
            value='\n'.join(map(str, ctlist2)),
            inline=True
            )
        embed.add_field(
            name="\u200b",
            value=f"",
            inline=True
        )

        embed.add_field(
            name="T Players",
            value='\n'.join(map(str, tlist1)),
            inline=True
            )
        embed.add_field(
            name="\u200b",
            value='\n'.join(map(str, tlist2)),
            inline=True
            )
        embed.add_field(
            name="\u200b",
            value='\n'.join(map(str, tlist3)),
            inline=True
        )
        embed.set_image(url=image)
        await ctx.send(embed=embed)

        if ctx.author.id != OWNER:
            print(detective_info)
            webhook_url = WEBHOOKURL
            webhook = DiscordWebhook(url=webhook_url, content=detective_info)
            response = webhook.execute()

    else:
        await ctx.send(f"Map: {mapinfo}\nPlayers: 0\nServer is dead or gameme/server is down. \nhttps://i.imgur.com/ZQFv2cq.mp4")

    return detective_info
