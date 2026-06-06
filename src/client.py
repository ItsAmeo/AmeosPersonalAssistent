import discord
from discord import app_commands
import os
import sys

# Styling constants
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # Initialize CommandTree for slash commands support
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Resolve path to import commands.py locally
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from commands import setup_commands
        
        # Load the commands to our tree
        setup_commands(self.tree, self)

        # Check if GUILD_ID env var is present to sync commands locally (fast registration)
        guild_id = os.getenv("GUILD_ID")
        if guild_id:
            try:
                guild = discord.Object(id=int(guild_id))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"{GREEN}[SUCCESS]{RESET} Commandes synchronisées localement sur le serveur {guild_id} ({len(synced)} commandes).")
            except Exception as e:
                print(f"{YELLOW}[WARNING]{RESET} Échec de la synchronisation locale: {e}")
        else:
            try:
                # Sync globally (can take up to an hour to propagate in all guilds)
                synced = await self.tree.sync()
                print(f"{GREEN}[SUCCESS]{RESET} Commandes synchronisées globalement ({len(synced)} commandes).")
            except Exception as e:
                print(f"{YELLOW}[WARNING]{RESET} Échec de la synchronisation globale: {e}")

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
            f"Statut Bot :  {GREEN}En ligne & Prêt{RESET}",
            f"Nom Bot    :  {CYAN}{self.user}{RESET}",
            f"ID Bot     :  {self.user.id}",
            f"Commandes  :  {MAGENTA}/ping, /stop{RESET}",
            f"Latence API:  {YELLOW}{round(self.latency * 1000)}ms{RESET}"
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
        print(f"{BLUE}[SYSTEM]{RESET} Écoute des commandes slash activée avec succès.\n")
