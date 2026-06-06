import discord
from discord.ext import commands
import os
import sys
import time
import random
import json
import uuid
import re
import datetime
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

WARNS_FILE = "warns.json"

# Helper functions for warnings database
def load_warns():
    if not os.path.exists(WARNS_FILE):
        return {}
    try:
        with open(WARNS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except Exception:
        return {}

def save_warns(data):
    try:
        with open(WARNS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving warns.json: {e}")

# Helper function for duration parsing (e.g. 10m, 2h, 1d)
def parse_duration(duration_str: str) -> datetime.timedelta:
    match = re.match(r"^(\d+)([smhd])$", duration_str.lower())
    if not match:
        raise ValueError("Invalid duration format. Use e.g. 10m, 2h, 1d.")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    if unit == 's':
        return datetime.timedelta(seconds=amount)
    elif unit == 'm':
        return datetime.timedelta(minutes=amount)
    elif unit == 'h':
        return datetime.timedelta(hours=amount)
    elif unit == 'd':
        return datetime.timedelta(days=amount)
    else:
        raise ValueError("Invalid unit. Use s, m, h, or d.")

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Home", description="Go back to the help menu home page.", emoji="📖", value="home"),
            discord.SelectOption(label="Utilities", description="Information and utility commands.", emoji="🛠️", value="utils"),
            discord.SelectOption(label="Moderation", description="Commands to manage the server.", emoji="⚖️", value="mod"),
            discord.SelectOption(label="Entertainment", description="Games and fun commands.", emoji="🎮", value="fun")
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
            name="⚖️ Moderation Tools",
            value="`+warn`, `+unwarn`, `+warns`, `+mute`, `+unmute`, `+kick`, `+ban`, `+unban`, `+softban`, `+lock`, `+unlock`, `+slowmode`",
            inline=False
        )
        embed.add_field(
            name="🎮 Entertainment",
            value="`+roll`, `+8ball`",
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
        embed.add_field(name="`+warn <member> <reason>`", value="Warns a member, logs it with a unique Warn ID in warns.json, and DMs them.", inline=False)
        embed.add_field(name="`+unwarn <warn_id>`", value="Removes a specific warning from the user using its Warn ID.", inline=False)
        embed.add_field(name="`+warns <member>`", value="Lists all active warnings for the given member.", inline=False)
        embed.add_field(name="`+mute <member> <duration> [reason]`", value="Tempmutes (timeouts) a member (e.g., `10m`, `2h`, `1d`). Max: 28 days.", inline=False)
        embed.add_field(name="`+unmute <member> [reason]`", value="Removes mute (timeout) from a member.", inline=False)
        embed.add_field(name="`+kick <member> [reason]`", value="Kicks the targeted member from the server.", inline=False)
        embed.add_field(name="`+ban <member> [reason]`", value="Permanently bans the targeted member from the server.", inline=False)
        embed.add_field(name="`+unban <user_id> [reason]`", value="Unbans a user from the server using their User ID.", inline=False)
        embed.add_field(name="`+softban <member> [reason]`", value="Bans and immediately unbans a member to prune their messages from the last 7 days.", inline=False)
        embed.add_field(name="`+lock [reason]`", value="Locks the current channel so default members cannot send messages.", inline=False)
        embed.add_field(name="`+unlock`", value="Unlocks the current channel.", inline=False)
        embed.add_field(name="`+slowmode <seconds>`", value="Sets slowmode cooldown (0 to 21600 seconds) for the current channel.", inline=False)
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

    @bot.command(name="unban", help="Unbans a user from the server using their ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, user_id: int, *, reason: str = "No reason provided"):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="🔓 User Unbanned",
                description=f"**{user.name}** (ID: {user_id}) has been unbanned.",
                color=0x2ECC71
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                title="⚠️ Unban Error",
                description="This user is not banned or does not exist.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Unban Error",
                description=f"Could not unban this user: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="softban", help="Bans and immediately unbans a member to prune their messages.")
    @commands.has_permissions(ban_members=True)
    async def softban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You cannot softban this member because they possess a role equivalent to or higher than yours.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return

        try:
            embed_dm = discord.Embed(
                title="🚪 Softban",
                description=f"You have been softbanned from **{ctx.guild.name}**.",
                color=0xE74C3C
            )
            embed_dm.add_field(name="Reason", value=reason)
            await member.send(embed=embed_dm)
        except Exception:
            pass

        try:
            await ctx.guild.ban(member, reason=f"Softban: {reason}", delete_message_seconds=604800)
            await ctx.guild.unban(member, reason="Softban cleanup")
            
            embed = discord.Embed(
                title="🧽 Member Softbanned",
                description=f"**{member.name}** has been softbanned (kicked and messages pruned).",
                color=0x2ECC71
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Softban Error",
                description=f"Could not softban this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="warn", help="Warns a member and logs it in the system with a unique ID.")
    @commands.has_permissions(kick_members=True)
    async def warn(ctx, member: discord.Member, *, reason: str):
        warn_id = str(uuid.uuid4())[:8]
        timestamp = time.time()
        
        guild_id_str = str(ctx.guild.id)
        user_id_str = str(member.id)
        
        warns_data = load_warns()
        if guild_id_str not in warns_data:
            warns_data[guild_id_str] = {}
        if user_id_str not in warns_data[guild_id_str]:
            warns_data[guild_id_str][user_id_str] = []
            
        warn_entry = {
            "warn_id": warn_id,
            "reason": reason,
            "moderator_id": ctx.author.id,
            "moderator_name": ctx.author.name,
            "timestamp": timestamp
        }
        
        warns_data[guild_id_str][user_id_str].append(warn_entry)
        save_warns(warns_data)
        
        try:
            embed_dm = discord.Embed(
                title="⚠️ Warning Received",
                description=f"You have received a warning on the server **{ctx.guild.name}**.",
                color=0xF1C40F
            )
            embed_dm.add_field(name="Reason", value=reason, inline=False)
            embed_dm.add_field(name="Given by", value=ctx.author.name, inline=True)
            embed_dm.add_field(name="Warn ID", value=f"`{warn_id}`", inline=True)
            await member.send(embed=embed_dm)
        except Exception:
            pass
            
        embed = discord.Embed(
            title="⚠️ Warning Registered",
            description=f"**{member.name}** has been warned.",
            color=0xF1C40F
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Warn ID", value=f"`{warn_id}`", inline=True)
        await ctx.send(embed=embed)

    @bot.command(name="warns", help="Lists all warnings of a user.")
    @commands.has_permissions(kick_members=True)
    async def warns(ctx, member: discord.Member):
        guild_id_str = str(ctx.guild.id)
        user_id_str = str(member.id)
        
        warns_data = load_warns()
        user_warns = warns_data.get(guild_id_str, {}).get(user_id_str, [])
        
        if not user_warns:
            embed = discord.Embed(
                title="📭 No Warnings Found",
                description=f"**{member.name}** has no registered warnings.",
                color=0x2ECC71
            )
            await ctx.send(embed=embed)
            return
            
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.name} ({len(user_warns)})",
            color=0xF1C40F
        )
        
        for w in user_warns:
            t = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(w['timestamp']))
            embed.add_field(
                name=f"ID: `{w['warn_id']}`",
                value=f"**Reason:** {w['reason']}\n**Mod:** {w['moderator_name']} (ID: {w['moderator_id']})\n**Date:** {t}",
                inline=False
            )
            
        await ctx.send(embed=embed)

    @bot.command(name="unwarn", help="Removes a warning using its unique Warn ID.")
    @commands.has_permissions(kick_members=True)
    async def unwarn(ctx, warn_id: str):
        guild_id_str = str(ctx.guild.id)
        warns_data = load_warns()
        
        guild_warns = warns_data.get(guild_id_str, {})
        found = False
        target_user_id = None
        target_warn = None
        
        for user_id, user_list in guild_warns.items():
            for w in user_list:
                if w['warn_id'] == warn_id:
                    target_user_id = user_id
                    target_warn = w
                    user_list.remove(w)
                    found = True
                    break
            if found:
                break
                
        if found:
            if not guild_warns[target_user_id]:
                del guild_warns[target_user_id]
            if not warns_data[guild_id_str]:
                del warns_data[guild_id_str]
                
            save_warns(warns_data)
            
            try:
                member_user = await bot.fetch_user(int(target_user_id))
                member_name = member_user.name
            except Exception:
                member_name = f"ID: {target_user_id}"
                
            embed = discord.Embed(
                title="🔓 Warning Removed",
                description=f"Warning `{warn_id}` has been removed.",
                color=0x2ECC71
            )
            embed.add_field(name="Belonged to", value=member_name, inline=True)
            embed.add_field(name="Reason", value=target_warn['reason'], inline=True)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Warning Not Found",
                description=f"No warning with ID `{warn_id}` was found in this server.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="mute", help="Mutes (timeouts) a member for a set duration. Format: +mute <member> <duration> [reason] (e.g. 10m, 1h, 1d)")
    @commands.has_permissions(moderate_members=True)
    async def mute(ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You cannot mute this member because they possess a role equivalent to or higher than yours.",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)
            return

        try:
            delta = parse_duration(duration)
            if delta.days > 28:
                raise ValueError("Max duration is 28 days.")
        except ValueError as e:
            embed = discord.Embed(
                title="⚠️ Invalid Duration",
                description=f"{e}\nUsage: `+mute <member> <duration> [reason]` (e.g., `10m`, `2h`, `1d`).",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(delta, reason=reason)
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member.name}** has been muted for `{duration}`.",
                color=0x2ECC71
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Muted until", value=discord.utils.format_dt(discord.utils.utcnow() + delta, style='R'), inline=False)
            await ctx.send(embed=embed)
            
            try:
                embed_dm = discord.Embed(
                    title="🔇 Muted",
                    description=f"You have been muted in **{ctx.guild.name}** for `{duration}`.",
                    color=0xE74C3C
                )
                embed_dm.add_field(name="Reason", value=reason)
                await member.send(embed=embed_dm)
            except Exception:
                pass
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Mute Error",
                description=f"Could not mute this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="unmute", help="Unmutes (removes timeout from) a member.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if not member.is_timed_out():
            embed = discord.Embed(
                title="⚠️ Member Not Muted",
                description=f"**{member.name}** is not currently muted.",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return

        try:
            await member.timeout(None, reason=reason)
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member.name}** has been unmuted.",
                color=0x2ECC71
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
            
            try:
                embed_dm = discord.Embed(
                    title="🔊 Unmuted",
                    description=f"You have been unmuted in **{ctx.guild.name}**.",
                    color=0x2ECC71
                )
                await member.send(embed=embed_dm)
            except Exception:
                pass
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Unmute Error",
                description=f"Could not unmute this member: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="lock", help="Locks the current channel so members cannot send messages.")
    @commands.has_permissions(manage_channels=True)
    async def lock(ctx, *, reason: str = "No reason provided"):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.send_messages is False:
            embed = discord.Embed(
                title="⚠️ Channel Already Locked",
                description="This channel is already locked.",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return

        overwrite.send_messages = False
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"This channel has been locked.",
                color=0xE74C3C
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Lock Error",
                description=f"Could not lock this channel: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="unlock", help="Unlocks the current channel so members can send messages again.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(ctx):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.send_messages is not False:
            embed = discord.Embed(
                title="⚠️ Channel Already Unlocked",
                description="This channel is not locked.",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return

        overwrite.send_messages = None
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason="Channel unlocked")
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="This channel has been unlocked.",
                color=0x2ECC71
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Unlock Error",
                description=f"Could not unlock this channel: {e}",
                color=0xE74C3C
            )
            await ctx.send(embed=embed)

    @bot.command(name="slowmode", help="Sets the slowmode (cooldown) in seconds for the current channel.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(ctx, seconds: int):
        if seconds < 0 or seconds > 21600:
            embed = discord.Embed(
                title="⚠️ Invalid Slowmode Value",
                description="Please specify a number between 0 (disabled) and 21600 (6 hours).",
                color=0xF1C40F
            )
            await ctx.send(embed=embed)
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            if seconds == 0:
                embed = discord.Embed(
                    title="⏲️ Slowmode Disabled",
                    description="Slowmode has been disabled for this channel.",
                    color=0x2ECC71
                )
            else:
                embed = discord.Embed(
                    title="⏲️ Slowmode Updated",
                    description=f"Slowmode has been set to `{seconds}` seconds.",
                    color=0x2ECC71
                )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Slowmode Error",
                description=f"Could not set slowmode: {e}",
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
        self.remove_command('help')
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
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print(f"{RED}[ERROR] DISCORD_TOKEN is not defined in the .env file!{RESET}")
        print("Please edit the .env file and paste your Discord bot token.")
        sys.exit(1)
        
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = MyBot(command_prefix="+", intents=intents)
    
    try:
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
