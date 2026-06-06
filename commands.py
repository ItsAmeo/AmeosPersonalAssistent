import discord
from discord import app_commands
import time

# Styling constants
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
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
