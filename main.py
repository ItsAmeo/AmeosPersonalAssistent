import discord
from discord.ext import commands
import os
import sys
import time
import random
from dotenv import load_dotenv

# Styling constants
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Home", description="Go back to the help menu home page.", emoji="📖", value="home"),
            discord.SelectOption(label="Utilities", description="Information and utility commands.", emoji="🛠️", value="utils"),
            discord.SelectOption(label="Moderation", description="Commands to manage the server.", emoji="⚖️", value="mod"),
            discord.SelectOption(label="Entertainment", description="Games and fun commands.", emoji="🎮", value="fun"),
            discord.SelectOption(label="System", description="System administration commands.", emoji="⚙️", value="sys")
        ]
        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        embed = get_help_embed(value, self.bot, interaction.user)
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=120)
        self.bot = bot
        self.author = author
        self.message = None
        self.add_item(HelpDropdown(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ You cannot use this help menu, please run your own `+help` command.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                item.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)
        except Exception:
            pass

def get_help_embed(category: str, bot, user) -> discord.Embed:
    avatar_url = bot.user.avatar.url if bot.user.avatar else None
    user_avatar = user.display_avatar.url if user.display_avatar else None

    if category == "home":
        embed = discord.Embed(
            title="📖 Help Menu - AmeoPersonalAssistant",
            description=(
                "Welcome to the **AmeoPersonalAssistant** help menu!\n\n"
                "This bot is now configured with the `+` prefix for all its commands.\n"
                "Use the dropdown menu below to explore the features by category."
            ),
            color=0x1F85DE # Sleek royal blue
        )
        embed.add_field(
            name="🛠️ Utilities & Info",
            value="`+help`, `+ping`, `+userinfo`, `+serverinfo`, `+avatar`, `+clear`",
            inline=False
        )
        embed.add_field(
            name="⚖️ Moderation",
            value="`+kick`, `+ban`, `+warn`",
            inline=False
        )
        embed.add_field(
            name="🎮 Entertainment",
            value="`+roll`, `+8ball`",
            inline=False
        )
        embed.add_field(
            name="⚙️ System",
            value="`+stop`",
            inline=False
        )
        embed.set_footer(text="Choose a category in the dropdown menu below!", icon_url=user_avatar)
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        return embed

    elif category == "utils":
        embed = discord.Embed(
            title="🛠️ Utilities & Information",
            description="Here are the utility commands available on the bot:",
            color=0x3498DB
        )
        embed.add_field(name="`+help`", value="Displays this interactive help menu.", inline=False)
        embed.add_field(name="`+ping`", value="Displays the bot's WebSocket latency and API response time.", inline=False)
        embed.add_field(name="`+userinfo [member]`", value="Displays details of a member (creation date, roles, etc.).", inline=False)
        embed.add_field(name="`+serverinfo`", value="Displays detailed information about the current server.", inline=False)
        embed.add_field(name="`+avatar [member]`", value="Displays a member's full-size profile picture.", inline=False)
        embed.add_field(name="`+clear <amount>`", value="Deletes a specified number of messages in the channel (1 to 100).", inline=False)
        embed.set_footer(text="Category: Utilities", icon_url=user_avatar)
        return embed

    elif category == "mod":
        embed = discord.Embed(
            title="⚖️ Moderation Tools",
            description="Commands to ensure the safety and organization of your server:",
            color=0xE67E22
        )
        embed.add_field(name="`+kick <member> [reason]`", value="Kicks the targeted member from the server.", inline=False)
        embed.add_field(name="`+ban <member> [reason]`", value="Permanently bans the targeted member from the server.", inline=False)
        embed.add_field(name="`+warn <member> <reason>`", value="Sends a formal warning via DM to the member and notifies in the chat.", inline=False)
        embed.set_footer(text="Category: Moderation", icon_url=user_avatar)
        return embed

    elif category == "fun":
        embed = discord.Embed(
            title="🎮 Entertainment & Fun",
            description="Add some fun and activities to your server:",
            color=0x9B59B6
        )
        embed.add_field(name="`+roll [max]`", value="Rolls a virtual die. Default maximum value is 100.", inline=False)
        embed.add_field(name="`+8ball <question>`", value="Ask the Magic 8-Ball a question and get a mystical response.", inline=False)
        embed.set_footer(text="Category: Entertainment", icon_url=user_avatar)
        return embed

    elif category == "sys":
        embed = discord.Embed(
            title="⚙️ System Commands",
            description="Internal bot administration options:",
            color=0xE74C3C
        )
        embed.add_field(name="`+stop`", value="Cleanly stops the Discord bot. Accessible only to the bot owner or server administrators.", inline=False)
        embed.set_footer(text="Category: System", icon_url=user_avatar)
        return embed

def setup_commands(bot: commands.Bot):
    @bot.command(name="ping", help="Displays the bot's latency.")
    async def ping(ctx):
        ws_latency = round(bot.latency * 1000)
        
        start_time = time.time()
        async with ctx.typing():
            end_time = time.time()
            api_latency = round((end_time - start_time) * 1000)
            
            embed = discord.Embed(
                title="🏓 Pong!",
                description="Here are the bot's connection statistics.",
                color=0x5865F2 # Discord Blurple
            )
            
            embed.add_field(
                name="⚡ WebSocket",
                value=f"`{ws_latency} ms`",
                inline=True
            )
            
            embed.add_field(
                name="🌐 API Latency",
                value=f"`{api_latency} ms`",
                inline=True
            )
            
            status_color = "🟢 Stable" if ws_latency < 150 else ("🟡 Average" if ws_latency < 300 else "🔴 High")
            embed.add_field(
                name="📊 Signal Status",
                value=f"`{status_color}`",
                inline=False
            )
            
            if bot.user.avatar:
                embed.set_thumbnail(url=bot.user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
                
            await ctx.send(embed=embed)

    @bot.command(name="stop", help="Cleanly stops the bot.")
    async def stop(ctx):
        is_owner = False
        try:
            app_info = await bot.application_info()
            is_owner = (ctx.author.id == app_info.owner.id) or (app_info.team and ctx.author.id in [m.id for m in app_info.team.members])
        except Exception:
            pass
            
        is_admin = ctx.author.guild_permissions.administrator if ctx.guild else False
        
        if not (is_owner or is_admin):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="Only server administrators or the bot owner can execute this command.",
                color=0xE74C3C # Red
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="🔌 Disconnecting...",
            description="The bot is shutting down cleanly. Thank you for using **AmeoPersonalAssistant**!",
            color=0xE74C3C # Red
        )
        
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
            
        await ctx.send(embed=embed)
        
        print(f"\n{RED}[SYSTEM] Stop signal received from {ctx.author} (ID: {ctx.author.id}).{RESET}")
        print(f"{YELLOW}[SYSTEM] Closing connection with Discord...{RESET}")
        
        await bot.close()
        print(f"{GREEN}[SUCCESS] Connection closed. The bot is offline.{RESET}")

    @bot.command(name="help", help="Displays the list of all available commands.")
    async def help_cmd(ctx):
        view = HelpView(bot, ctx.author)
        embed = get_help_embed("home", bot, ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @bot.command(name="userinfo", help="Displays details of a user.")
    async def userinfo(ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        roles_str = " ".join(roles) if roles else "No roles"
        
        embed = discord.Embed(
            title=f"👤 Info on {member.name}",
            color=member.color if member.color.value != 0 else 0x3498DB
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
            
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Bot?", value="Yes" if member.bot else "No", inline=True)
        
        created_at = member.created_at.strftime("%m/%d/%Y %H:%M:%S")
        joined_at = member.joined_at.strftime("%m/%d/%Y %H:%M:%S") if member.joined_at else "Unknown"
        
        embed.add_field(name="Created on", value=created_at, inline=False)
        embed.add_field(name="Joined on", value=joined_at, inline=False)
        embed.add_field(name=f"Roles ({len(roles)})", value=roles_str, inline=False)
        await ctx.send(embed=embed)

    @bot.command(name="serverinfo", help="Displays server details.")
    async def serverinfo(ctx):
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used inside a server.")
            return
            
        embed = discord.Embed(
            title=f"🏰 Info on server {guild.name}",
            color=0x3498DB
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else f"ID: {guild.owner_id}", inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles_count = len(guild.roles) - 1
        
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Roles", value=roles_count, inline=True)
        
        created_at = guild.created_at.strftime("%m/%d/%Y %H:%M:%S")
        embed.add_field(name="Created on", value=created_at, inline=False)
        await ctx.send(embed=embed)

    @bot.command(name="clear", help="Deletes a defined number of messages in the channel.")
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int):
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="⚠️ Invalid Limit",
                description="Please specify a number between 1 and 100.",
                color=0xF1C40F
            )
            await ctx.send(embed=embed, delete_after=5)
            return
            
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        
        embed = discord.Embed(
            title="🧹 Cleanup Finished",
            description=f"`{len(deleted)}` messages were deleted.",
            color=0x2ECC71
        )
        await ctx.send(embed=embed, delete_after=5)

    @bot.command(name="kick", help="Kicks a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You cannot kick this member because they possess a role equivalent to or higher than yours.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return
            
        try:
            embed_dm = discord.Embed(
                title="🚪 Kick",
                description=f"You have been kicked from the server **{ctx.guild.name}**.",
                color=0xE74C3C
            )
            embed_dm.add_field(name="Reason", value=reason)
            await member.send(embed=embed_dm)
        except Exception:
            pass
            
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member.name}** has been kicked by **{ctx.author.name}**.",
                color=0x2ECC71
            )
            embed.add_field(name="Reason", value=reason)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Kick Error",
                description=f"Could not kick this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="ban", help="Bans a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You cannot ban this member because they possess a role equivalent to or higher than yours.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return
            
        try:
            embed_dm = discord.Embed(
                title="🔨 Ban",
                description=f"You have been banned from the server **{ctx.guild.name}**.",
                color=0xE74C3C
            )
            embed_dm.add_field(name="Reason", value=reason)
            await member.send(embed=embed_dm)
        except Exception:
            pass
            
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member.name}** has been banned by **{ctx.author.name}**.",
                color=0xE74C3C
            )
            embed.add_field(name="Reason", value=reason)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Ban Error",
                description=f"Could not ban this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="warn", help="Warns a member.")
    @commands.has_permissions(kick_members=True)
    async def warn(ctx, member: discord.Member, *, reason: str):
        try:
            embed_dm = discord.Embed(
                title="⚠️ Warning",
                description=f"You have received a warning on the server **{ctx.guild.name}**.",
                color=0xF1C40F
            )
            embed_dm.add_field(name="Reason", value=reason)
            embed_dm.add_field(name="Given by", value=ctx.author.name)
            await member.send(embed=embed_dm)
            
            embed = discord.Embed(
                title="⚠️ Warning Registered",
                description=f"**{member.name}** has received a warning.",
                color=0xF1C40F
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=ctx.author.mention)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Warning Error",
                description=f"Could not send the warning to this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="avatar", help="Displays a member's profile picture.")
    async def avatar(ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(
            title=f"🖼️ Avatar of {member.name}",
            color=0x3498DB
        )
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)

    @bot.command(name="roll", help="Rolls a random die.")
    async def roll(ctx, max_val: int = 100):
        if max_val < 1:
            embed = discord.Embed(
                title="⚠️ Invalid Value",
                description="The maximum value must be greater than 0.",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return
        result = random.randint(1, max_val)
        embed = discord.Embed(
            title="🎲 Die Roll!",
            description=f"**{ctx.author.name}** rolled a die (1-{max_val}) and got:",
            color=0x9B59B6
        )
        embed.add_field(name="Result", value=f"🏆 **{result}**", inline=False)
        await ctx.send(embed=embed)

    @bot.command(name="8ball", help="Asks the Magic 8-Ball a question.")
    async def magic_8ball(ctx, *, question: str):
        responses = [
            "Try again later.", "Try again.", "No opinion.", "It is your destiny.",
            "The die is cast.", "A fifty-fifty chance.", "Ask your question again.",
            "In my opinion, yes.", "It is certain.", "Yes, absolutely.", "You can count on it.",
            "Without a doubt.", "Most likely.", "Yes.", "Looking good.",
            "No.", "Unlikely.", "Don't count on it.", "Impossible.", "Don't rely on it."
        ]
        response = random.choice(responses)
        embed = discord.Embed(
            title="🔮 Magic 8-Ball",
            color=0x2C3E50
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Response", value=f"🎱 **{response}**", inline=False)
        await ctx.send(embed=embed)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
            
        embed = discord.Embed(
            title="❌ Execution Error",
            color=0xE74C3C
        )
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"Missing argument: `{error.param.name}`. Please check command syntax."
        elif isinstance(error, commands.BadArgument):
            embed.description = "One or more arguments provided are invalid (e.g. Member not found)."
        elif isinstance(error, commands.MissingPermissions):
            permissions = ", ".join(f"`{perm}`" for perm in error.missing_permissions)
            embed.description = f"You do not possess the required permissions to execute this command.\nMissing permissions: {permissions}"
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = ", ".join(f"`{perm}`" for perm in error.missing_permissions)
            embed.description = f"The bot does not have the required permissions to execute this operation.\nMissing permissions: {permissions}"
        else:
            embed.description = f"An error occurred: {error}"
            
        await ctx.send(embed=embed, delete_after=15)

class MyBot(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        # Remove default help command
        self.remove_command('help')
        
        # Load commands
        setup_commands(self)

    async def on_ready(self):
        # Display a beautiful startup ASCII logo and bot statistics box
        logo = rf"""{BLUE}{BOLD}
    ___    __  _________  ____  ____  ____  ______
   /   |  /  |/  / ____/ / __ \/ __ \/ __ \/_  __/
   / /| | / /|_/ / __/   / / / / /_/ / / / / / /   
  / ___ |/ /  / / /___  / /_/ / ____/ /_/ / / /    
/_/  |_/_/  /_/_____/  \____/_/    \____/ /_/     
                                                  {RESET}"""
        print(logo)
        
        info_lines = [
            f"Bot Status :  {GREEN}Online & Ready{RESET}",
            f"Bot Name   :  {CYAN}{self.user}{RESET}",
            f"Bot ID     :  {self.user.id}",
            f"Prefix     :  {MAGENTA}{self.command_prefix}{RESET}",
            f"Commands   :  {MAGENTA}{len(self.commands)} Active commands{RESET}",
            f"API Latency:  {YELLOW}{round(self.latency * 1000)}ms{RESET}"
        ]
        
        # Calculate maximum display length without ANSI formatting codes
        def clean_ansi(text):
            for code in [GREEN, CYAN, MAGENTA, YELLOW, BLUE, RESET, BOLD]:
                text = text.replace(code, "")
            return text
            
        max_len = max(len(clean_ansi(line)) for line in info_lines)
        border = "─" * (max_len + 4)
        
        print(f"┌{border}┐")
        for line in info_lines:
            padding = " " * (max_len - len(clean_ansi(line)))
            print(f"│  {line}{padding}  │")
        print(f"└{border}┘")
        print(f"{BLUE}[SYSTEM]{RESET} Listening for commands with prefix '{self.command_prefix}' successfully enabled.\n")

def main():
    # Load environment variables from .env
    load_dotenv()
    
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print(f"{RED}[ERROR] DISCORD_TOKEN is not defined in the .env file!{RESET}")
        print("Please edit the .env file and paste your Discord bot token.")
        sys.exit(1)
        
    # Configure default intents and enable message content intent
    intents = discord.Intents.default()
    intents.message_content = True
    
    # Initialize our custom bot
    bot = MyBot(command_prefix="+", intents=intents)
    
    try:
        # Start the bot
        bot.run(token)
    except discord.errors.LoginFailure:
        print(f"\n{RED}[ERROR] Login failed. The DISCORD_TOKEN provided in the .env file is invalid.{RESET}")
        print("Please check your token on the Discord Developer Portal.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}[ERROR] An unexpected error occurred during startup: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
