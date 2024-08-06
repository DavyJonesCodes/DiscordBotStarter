from discord import Interaction
from discord.ext import commands
from jsonDB import JsonDB
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from a .env file
load_dotenv()
DATABASE: Optional[str] = os.getenv('DATABASE')


class Utils:
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.db = JsonDB(DATABASE)  # Initialize the JSON database

    async def logger(self, interaction: Interaction, **kwargs):
        """Log the interaction details to the log channel."""
        # Check if the log channel is set in the database
        log_channel_id = self.db['utils'].get('log_channel')
        if not log_channel_id:
            return

        # Build the log message
        message = (
            f"# LOG\n"
            f"```js\n"
            f"Username: `{interaction.user.name}#{interaction.user.discriminator}`\n"
            f"UserID: {interaction.user.id}\n"
            f"Guild Name: `{interaction.guild.name if interaction.guild else 'Direct message'}`\n"
            f"GuildID: {interaction.guild.id if interaction.guild else 'Direct message'}\n"
            f"Command: /{interaction.command.qualified_name}\n"
            f"```"
        )

        if kwargs:
            message += "\n**ARGS**\n```js"
            for key, value in kwargs.items():
                message += f"\n{key}: {value}"
            message += "\n```"

        # Fetch the log channel and check if the bot has permissions to send messages
        log_channel = self.client.get_channel(log_channel_id)
        if log_channel and log_channel.permissions_for(log_channel.guild.me).send_messages:
            await log_channel.send(message)
        else:
            raise PermissionError(f"Unable to send log message to channel <#{log_channel_id}>. Check permissions or channel existence.")
