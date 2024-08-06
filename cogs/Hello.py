import discord
from discord import Interaction, app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables from a .env file
load_dotenv()
TOKEN: Optional[str] = os.getenv('TOKEN')


class HelloButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # Add a button to the view
        self.button = discord.ui.Button(label="Click Me!", style=discord.ButtonStyle.primary, custom_id="hello_button")
        self.button.callback = self.hello_button_callback
        self.add_item(self.button)

    async def hello_button_callback(self, interaction: Interaction):
        """Handle button interaction."""
        await interaction.response.send_message("Hello! You clicked the button.", ephemeral=True)


class Hello(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="hello", description="Send a hello message with a button")
    @app_commands.guild_only()
    async def hello(self, interaction: Interaction):
        """Command to send a hello message with a button."""
        await interaction.response.send_message("Hello!", view=HelloButton(), ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Hello(client))
