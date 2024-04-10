import os
import discord
import requests
import xml.etree.ElementTree as ET
import json
import aiohttp
from discord.ext import commands
from discord import app_commands
from discord_webhook import DiscordWebhook

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

with open('config.json') as config_file:
    config_data = json.load(config_file)
WEBHOOKURL = config_data['webhook']

XML_API_URL = 'https://edgegamers.gameme.com/api/serverinfo/104.128.58.156:27015/players'

def scrape_xml():
    response = requests.get(XML_API_URL)
    if response.status_code == 200:
        root = ET.fromstring(response.content)

        # Find the <map> element
        map_info = root.find('.//server/map').text

        # Initialize empty lists for both teams
        ct_player = []
        t_player = []

        # Iterate through each player
        for player in root.findall('.//server/players/player'):
            player_name = player.find('name').text
            player_team = player.find('team').text

            # Depending on the team, append the player to the corresponding list
            if player_team == "CT":
                ct_player.append(player_name)
            elif player_team == "TERRORIST":
                t_player.append(player_name)
            # Optionally handle players without a team or with a different designation

        return map_info, ct_player, t_player
    else:
        return None, None, None  # Returning None values if fetching XML data fails


# Command: /players
@client.hybrid_command(help="Displays players on the server", usage="/players")
async def players(ctx: commands.Context):
    if ctx.guild is None:
        guild_name = "Private Messages"
    else:
        guild_name = ctx.guild.name  # Get guild name
        guild_id = ctx.guild.id # Get guild id
        guild_ownerid = ctx.guild.owner_id # Get owner of server id
        guild_owner = ctx.guild.owner # Get owner name

    # Get the current timestamp in UTC
    current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if ctx.guild is None:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /map \nServer: ({guild_name})' #this is for the webhook
    else:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /map \nName: ({guild_name}) \nID: ({guild_id}) \nOwner: ({guild_owner}) \nID: ({guild_ownerid})' #this is for the webhook

    map_info, ct_player, t_player = scrape_xml()
    if map_info is not None and ct_player is not None and t_player is not None:
        message = f"Map: {map_info}\n\nCT List:\n"
        for player in ct_player:
            message += f"{player}\n"

        message += "\nT List:\n"
        for player in t_player:
            message += f"{player}\n"

        await ctx.send(message)
    else:
        await ctx.send("Failed to fetch data")

# Print detective_info to the terminal
    print(detective_info)

    webhook_url = WEBHOOKURL 
    webhook = DiscordWebhook(url=webhook_url, content=detective_info) #this sends webhooks
    response = webhook.execute()

    return detective_info
