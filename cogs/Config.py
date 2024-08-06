from datetime import datetime, timezone
import discord
from discord import Interaction, app_commands, Embed
from discord.ext import commands
from jsonDB import JsonDB
import os
from dotenv import load_dotenv
from typing import Optional
from .Utils import Utils

# Load environment variables from a .env file
load_dotenv()
DATABASE: Optional[str] = os.getenv('DATABASE')


class DashboardControls(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client
        self.db = JsonDB(DATABASE)  # Initialize the JSON database

        # Log channel selection menu
        self.log_channel_select = discord.ui.ChannelSelect(
            placeholder="Select a new log channel", custom_id="dashboard1")
        self.log_channel_select.callback = self.log_channel_select_callback
        self.add_item(self.log_channel_select)

        # Backup channel selection menu
        self.backup_channel_select = discord.ui.ChannelSelect(
            placeholder="Select a new backup channel", custom_id="dashboard2")
        self.backup_channel_select.callback = self.backup_channel_select_callback
        self.add_item(self.backup_channel_select)

    async def update_message(self, message):
        """Update the dashboard message with the current settings."""
        await message.edit(content="", embed=await self.create_embed(), view=self)

    async def create_embed(self):
        """Create the embed for the dashboard."""
        embed = Embed(
            title="Dashboard",
            color=discord.Color.from_str("#d6ac73"),
            description="Welcome to the bot settings dashboard. Here you can view and update the key settings for your server.",
            timestamp=datetime.now(timezone.utc)
        )

        log_channel = f"<#{self.db['utils']['log_channel']}>" if self.db['utils']['log_channel'] else "None"
        embed.add_field(name="Log Channel", value=(
            f"- **Current Log Channel**: {log_channel}\n"
            f"- **Description**: The channel where all logs will be sent.\n"
        ), inline=False)

        backup_channel = f"<#{self.db['utils']['backup_channel']}>" if self.db['utils']['backup_channel'] else "None"
        embed.add_field(name="Data Backup Channel", value=(
            f"- **Current Backup Channel**: {backup_channel}\n"
            f"- **Description**: The channel where data backups will be sent.\n"
        ), inline=False)

        embed.set_footer(text='Last updated', icon_url=self.client.user.avatar.url)

        return embed

    async def embed_valid_checker(self, interaction):
        """Check if the embed is still valid."""
        if interaction.message.embeds:
            return True
        else:
            await interaction.message.edit(content="This embed is no longer valid.", view=None, embed=None)
            return False

    async def log_channel_select_callback(self, interaction: discord.Interaction):
        """Callback function for log channel selection."""
        await interaction.response.defer()

        if not await self.embed_valid_checker(interaction):
            return

        selected_channel_id = self.log_channel_select.values[0].id
        self.db['utils']['log_channel'] = int(selected_channel_id)
        await interaction.message.reply(content=f"Log channel set to <#{selected_channel_id}>")
        await self.update_message(interaction.message)

    async def backup_channel_select_callback(self, interaction: discord.Interaction):
        """Callback function for backup channel selection."""
        await interaction.response.defer()

        if not await self.embed_valid_checker(interaction):
            return

        selected_channel_id = self.backup_channel_select.values[0].id
        self.db['utils']['backup_channel'] = int(selected_channel_id)
        await interaction.message.reply(content=f"Backup channel set to <#{selected_channel_id}>")
        await self.update_message(interaction.message)


class Config(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)  # Initialize utility functions

    @app_commands.command(name="dashboard", description="To open the dashboard")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def dashboard(self, interaction: Interaction):
        """Command to open the dashboard."""
        await interaction.response.defer()
        await self.utils.logger(interaction)

        dash = DashboardControls(self.client)
        msg = await interaction.followup.send("Getting details...")
        await dash.update_message(msg)


async def setup(client: commands.Bot) -> None:
    """Setup function to add the cog and view."""
    client.add_view(DashboardControls(client))
    await client.add_cog(Config(client))
