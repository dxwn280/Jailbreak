import os
import discord
import requests
import xml.etree.ElementTree as ET
import json
import aiohttp
import re
from discord.ext import commands
from discord import app_commands
from discord_webhook import DiscordWebhook

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
    "lego": "https://i.imgur.com/NmWHQK0.png",
    "unknown": "https://media.discordapp.net/attachments/1152808650436522045/1228862165105250325/video.gif?ex=662d9613&is=661b2113&hm=db8815275b4e99ae71163ce0640e050dd112579bb9adad4452455cc476f9a571&",
}



def scrape_xml():
    response = requests.get(XML_API_URL)
    if response.status_code == 200:
        root = ET.fromstring(response.content)

        # Find the <map> element
        mapinfo = root.find('.//server/map').text
        playerinfo = root.find('.//server/act').text

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

        return mapinfo, tlist, ctlist, playerinfo
    else:
        return None, None, None  # Returning None values if fetching XML data fails



#command /players
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


    #thing to give me the image of the map
    image_data = ['avalanche', 'undertale', 'clouds', 'minecraft', 'quake', 'spy', 'peanut', 'vipinthemix', 'kwejsi', 'umbrella', "lego", "moti2"] #list of maps
    mapinfo = str(scrape_xml()) #get info from the scraper
    map_match = re.search(r"'(.+?)'", mapinfo) # dont get the point of this
    if map_match:
        map_name = map_match.group(1) #take first value, which will be the map
    else:
        map_name = "unknown"  # Default to "unknown" if map name cannot be gotten
    
    split_info = map_name.split('_') #split the name of the map so theres no _
    
    print("Split info:", split_info) #debuging
    
    def intersection(image_data, split_info):
        for value in split_info:
            if value in image_data: # checks if split_info is a subset of image_data, if it is a subset
                return value # it instantly returns the first value, this is just incase if two values of split_info match image_data (ex: jb_clouds_spy)
        return None 

    check3 = intersection(image_data, split_info) # this gives me the actual value of what the subset matches with the set
    
    if check3 is None: #if there is no value i.e. new map or i didnt update image_links & image_data
        image = image_links["unknown"] #then return unknown
    else: #otherwise use the corresponding image from image_links
        index = split_info.index(check3)
        image = image_links[check3]


    #split t's into their teams
    mapinfo, tlist, ctlist, playerinfo = scrape_xml()
    
    if playerinfo:
        midpoint1 = len(ctlist)//2 # for ct's, 2 lists
        midpoint2 = len(tlist)//3 # for t's, 3 lists
    
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

        
        #embed shit
        embed = discord.Embed(
            title=f"Click to connect\nMap: {mapinfo}",
            url="https://cs2browser.com/connect/104.128.58.156:27015",
            timestamp=current_time
        )
        embed.set_author(name=f"Players: {playerinfo}")

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
