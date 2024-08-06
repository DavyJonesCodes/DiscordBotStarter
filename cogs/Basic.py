import discord
from discord import Interaction, app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Optional
from main import COG_DIR

# Load environment variables from a .env file
load_dotenv()
DEVELOPER: Optional[int] = int(os.getenv('DEVELOPER')) if os.getenv('DEVELOPER') else None


class Basic(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="sync", description="To sync commands")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def sync(self, interaction: Interaction):
        """Command to sync application commands with Discord."""
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != DEVELOPER:
            await interaction.followup.send("Only the developer can use this command.")
            return

        msg = await interaction.followup.send("Syncing...")
        await self.client.tree.sync()
        await msg.edit(content="Commands synced!")

    @app_commands.command(name="refresh", description="To refresh commands")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def refresh(self, interaction: Interaction):
        """Command to refresh all command cogs."""
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != DEVELOPER:
            await interaction.followup.send("Only the developer can use this command.")
            return

        msg = await interaction.followup.send("Refreshing...")
        for cog_file in COG_DIR.glob("*.py"):
            if cog_file.stem not in ["__init__", "Utils"]:
                await self.client.reload_extension(f"cogs.{cog_file.stem}")
        await msg.edit(content="Commands refreshed!")

    @app_commands.command(name="ping", description="To check bot latency")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def ping(self, interaction: discord.Interaction):
        """Command to check the bot's latency."""
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != DEVELOPER:
            await interaction.followup.send("Only the developer can use this command.")
            return

        bot_latency = round(self.client.latency * 1000)
        await interaction.followup.send(f"Pong! {bot_latency} ms.")


async def setup(client: commands.Bot) -> None:
    """Function to set up the Basic cog."""
    await client.add_cog(Basic(client))
