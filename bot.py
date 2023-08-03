import datetime
import os
from typing import Optional

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

import api
import config

load_dotenv()

MY_GUILD = discord.Object(id=os.getenv('GUILD_ID'))

emojis = [
    ":first_place:",
    ":second_place:",
    ":third_place:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
    ":keycap_ten:"
]

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

        # start task running in the background
        self.update_votes.start()

    @tasks.loop(minutes=1)
    async def update_votes(self):
        if not config.get('channel') or not config.get('message'):
            return
        
        response = api.get_current_month()

        body = "Top 10 voters this month:\n"
        for i, voter in enumerate(response.voters[:10]):
            body += f"{emojis[i]} **{voter.username}**: {voter.votes}\n"

        embed = discord.Embed(
            title="Vote Leaderboard",
            description=body,
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )

        channel = self.get_channel(config.get('channel'))
        message = await channel.fetch_message(config.get('message'))

        await message.edit(content=" ", embed=embed)

    @update_votes.before_loop
    async def before_update_votes(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')


@client.tree.command()
@app_commands.describe(
    channel='The channel the bot will send vote updates to'
)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Sets the channel to send vote updates to."""
    config.set('channel', channel.id)
    response = await client.get_channel(channel.id).send(f'Something smells here...')
    config.set('message', response.id)

    # await interaction.response.send_message(f'Channel set to {channel.mention}')


client.run(os.getenv('TOKEN'))
