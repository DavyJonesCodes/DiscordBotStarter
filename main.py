import discord
from discord.ext import commands
from discord import app_commands
import traceback
import os
from dotenv import load_dotenv
from typing import List, Optional
import pathlib

# Load environment variables from a .env file
load_dotenv()

# Retrieve the bot token and developer ID from environment variables
TOKEN: Optional[str] = os.getenv('TOKEN')
DEVELOPER: Optional[int] = int(os.getenv('DEVELOPER')) if os.getenv('DEVELOPER') else None

# Define base directory and cog directory paths
BASE_DIR = pathlib.Path(__file__).parent
COG_DIR = BASE_DIR / "cogs"


class Client(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=commands.when_mentioned_or("?"), intents=discord.Intents.all())
        self.remove_command('help')  # Remove default help command
        self.tree.on_error = self.on_tree_error  # Set tree command error handler

    async def setup_hook(self) -> None:
        """Load extensions (cogs) during bot setup."""
        for cog_file in COG_DIR.glob("*.py"):
            if cog_file.stem not in ["__init__", "Utils"]:
                await self.load_extension(f"cogs.{cog_file.stem}")

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        await self.tree.sync()  # Sync application commands with Discord

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))

        print("\nBot is online.\n")

    async def send_error(self, error: List[str], guild: Optional[discord.Guild], user: discord.User, command: discord.app_commands.Command) -> None:
        """Send error details to the developer."""
        dev: Optional[discord.User] = self.get_user(DEVELOPER) or await self.fetch_user(DEVELOPER)

        if not dev:
            return

        error_str: str = ''.join(error).replace('```', "'''")
        message: str = (
            f"# ERROR\n\n"
            f"**Username**: {user.name}#{user.discriminator}\n"
            f"**User ID**: {user.id}\n"
            f"**Guild Name**: {guild.name if guild else 'DM'}\n"
            f"**Guild ID**: {guild.id if guild else 'DM'}\n"
            f"**Command**: /{command.qualified_name if command.qualified_name else None}\n\n"
            f"```py\n{error_str}```"
        )

        if len(message) > 2000:
            # Split the message into chunks if it's too long
            lines = message.splitlines(keepends=True)
            current_chunk = ""
            for line in lines:
                if len(current_chunk) + len(line) > 1990:
                    await dev.send(f"{current_chunk}```")
                    current_chunk = f"```py\n{line}"
                else:
                    current_chunk += line

            if current_chunk:
                await dev.send(f"{current_chunk}")
        else:
            await dev.send(message)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle errors for commands."""
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            full_error = traceback.format_exception(type(error), error, error.__traceback__)
            await self.send_error(full_error, ctx.guild, ctx.author, ctx.command)

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """Handle errors for application commands."""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message((
                f"Command is currently on cooldown! Try again in **{error.retry_after:.0f}** seconds!"
            ), ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message((
                "You're missing permissions to use this command."
            ), ephemeral=True)
        elif isinstance(error, app_commands.CheckFailure):
            if interaction.command.qualified_name == "verify":
                await interaction.response.send_message((
                    "This command is restricted to direct messages with the bot to ensure the privacy and security of your password and personal details."
                ), ephemeral=True)
            else:
                await interaction.response.send_message("You're not authorized to use this command.", ephemeral=True)
        else:
            full_error = traceback.format_exception(type(error), error, error.__traceback__)
            await self.send_error(full_error, interaction.guild, interaction.user, interaction.command)


def main() -> None:
    """Main entry point for the bot."""
    if not TOKEN:
        raise ValueError("TOKEN environment variable not set")

    client = Client()
    client.run(TOKEN)


if __name__ == "__main__":
    main()
