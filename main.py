import discord
from discord import app_commands
import os
import sys
import time
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

def setup_commands(tree: app_commands.CommandTree, client: discord.Client):
    @tree.command(name="ping", description="Affiche la latence du bot.")
    async def ping(interaction: discord.Interaction):
        # Measure WebSocket latency
        ws_latency = round(client.latency * 1000)
        
        # Initial defer to measure API round-trip latency
        start_time = time.time()
        await interaction.response.defer(ephemeral=False)
        end_time = time.time()
        
        api_latency = round((end_time - start_time) * 1000)
        
        # Create a beautiful styled embed
        embed = discord.Embed(
            title="🏓 Pong !",
            description="Voici les statistiques de connexion du bot.",
            color=0x5865F2 # Discord Blurple
        )
        
        embed.add_field(
            name="⚡ WebSocket",
            value=f"`{ws_latency} ms`",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Latence API",
            value=f"`{api_latency} ms`",
            inline=True
        )
        
        # Add nice layout design indicators
        status_color = "🟢 Stable" if ws_latency < 150 else ("🟡 Moyen" if ws_latency < 300 else "🔴 Élevé")
        embed.add_field(
            name="📊 Statut du Signal",
            value=f"`{status_color}`",
            inline=False
        )
        
        if client.user.avatar:
            embed.set_thumbnail(url=client.user.avatar.url)
            embed.set_footer(text=f"Requête par {interaction.user}", icon_url=interaction.user.display_avatar.url)
        else:
            embed.set_footer(text=f"Requête par {interaction.user}")
            
        await interaction.followup.send(embed=embed)

    @tree.command(name="stop", description="Arrête proprement le bot.")
    async def stop(interaction: discord.Interaction):
        # Check authorization (is_owner or Administrator permissions in guild)
        is_owner = False
        try:
            # Check if user is the bot application owner
            app_info = await client.application_info()
            is_owner = (interaction.user.id == app_info.owner.id) or (app_info.team and interaction.user.id in [m.id for m in app_info.team.members])
        except Exception:
            pass
            
        is_admin = interaction.user.guild_permissions.administrator if interaction.guild else False
        
        if not (is_owner or is_admin):
            embed = discord.Embed(
                title="🚫 Accès Refusé",
                description="Seuls les administrateurs du serveur ou le propriétaire du bot peuvent exécuter cette commande.",
                color=0xE74C3C # Red
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="🔌 Déconnexion en cours...",
            description="Le bot s'arrête proprement. Merci d'avoir utilisé **AmeoPersonalAssistant** !",
            color=0xE74C3C # Red
        )
        
        if client.user.avatar:
            embed.set_thumbnail(url=client.user.avatar.url)
            
        await interaction.response.send_message(embed=embed)
        
        print(f"\n{RED}[SYSTEM] Signal d'arrêt reçu de la part de {interaction.user} (ID: {interaction.user.id}).{RESET}")
        print(f"{YELLOW}[SYSTEM] Fermeture de la connexion avec Discord...{RESET}")
        
        # Cleanly disconnect from Discord
        await client.close()
        print(f"{GREEN}[SUCCESS] Connexion fermée. Le bot est hors ligne.{RESET}")

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # Initialize CommandTree for slash commands support
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
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

def main():
    # Load environment variables from .env
    load_dotenv()
    
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print(f"{RED}[ERROR] DISCORD_TOKEN n'est pas défini dans le fichier .env !{RESET}")
        print("Veuillez éditer le fichier .env et y coller votre token de bot Discord.")
        sys.exit(1)
        
    # Configure default intents
    intents = discord.Intents.default()
    
    # Initialize our custom client
    client = MyClient(intents=intents)
    
    try:
        # Start the bot
        client.run(token)
    except discord.errors.LoginFailure:
        print(f"\n{RED}[ERROR] Impossible de se connecter. Le DISCORD_TOKEN fourni dans le fichier .env est invalide.{RESET}")
        print("Veuillez vérifier votre token sur le portail des développeurs Discord.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}[ERROR] Une erreur inattendue est survenue au démarrage : {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
