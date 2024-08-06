import discord
from discord import Interaction, app_commands
from discord.ext import commands, tasks
import os
import hashlib
from dotenv import load_dotenv
from typing import Optional
from jsonDB import JsonDB
from datetime import datetime, timezone
import json

# Load environment variables from a .env file
load_dotenv()
DATABASE: Optional[str] = os.getenv('DATABASE')


class Backup(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.db = JsonDB(DATABASE)  # Initialize the JSON database
        self.backup_task.start()  # Start the backup task loop

    def cog_unload(self):
        """Cancel the backup task when the cog is unloaded."""
        self.backup_task.cancel()

    @tasks.loop(hours=24)
    async def backup_task(self):
        """Periodic task to send a backup every 24 hours."""
        await self.send_backup()

    @backup_task.before_loop
    async def before_backup(self):
        """Wait until the bot is ready before starting the backup task."""
        await self.client.wait_until_ready()

    def get_file_hash(self, data: dict) -> str:
        """Generate a SHA-256 hash for the JSON data."""
        hasher = hashlib.sha256()
        # Convert JSON data to string and encode to bytes
        data_str = json.dumps(data, sort_keys=True)
        hasher.update(data_str.encode('utf-8'))
        return hasher.hexdigest()

    async def send_backup(self):
        """Send the backup to the designated channel if the data has changed."""
        backup_channel_id = self.db['utils'].get('backup_channel')
        if not backup_channel_id:
            return

        # Load the current data from the JSON file
        stored_data = self.db.load_data()

        # Remove the file hash value from the data
        stored_hash = stored_data.get('utils').pop('file_hash', None)

        # Get the current hash of the data
        current_hash = self.get_file_hash(stored_data)

        # Compare hashes, if they match, no need to send the backup
        if current_hash == stored_hash:
            return

        backup_channel = self.client.get_channel(backup_channel_id)
        if backup_channel and backup_channel.permissions_for(backup_channel.guild.me).send_messages:
            # Get file size
            file_size = os.path.getsize(self.db.filename)
            file_size_kb = file_size / 1024  # Convert to KB

            # Create a Discord file
            with open(self.db.filename, 'rb') as file:
                discord_file = discord.File(file, filename='data.json')

            await backup_channel.send(content=(
                f"# Data Backup\n"
                f"**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"**File Size:** {file_size_kb:.2f} KB\n"
            ), file=discord_file)

            # Store the new hash in the database
            self.db['utils']['file_hash'] = current_hash

        else:
            raise PermissionError(
                f"Unable to send backup message to channel <#{backup_channel_id}>. Check permissions or channel existence.")

    @app_commands.command(name="backup", description="Manually trigger a backup")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def manual_backup(self, interaction: Interaction):
        """Command to manually trigger a backup."""
        await interaction.response.defer(ephemeral=True)

        await self.send_backup()

        backup_channel_id = self.db['utils'].get('backup_channel')
        await interaction.followup.send(f"Backup has been sent to the <#{backup_channel_id}>.")


async def setup(client: commands.Bot) -> None:
    """Set up the cog."""
    await client.add_cog(Backup(client))
