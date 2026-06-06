import discord
from discord import app_commands
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

    @tree.command(name="help", description="Affiche la liste de toutes les commandes disponibles.")
    async def help_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Menu d'Aide - AmeoPersonalAssistant",
            description="Voici la liste des commandes slash disponibles sur le bot :",
            color=0x3498DB
        )
        embed.add_field(
            name="🛠️ Utilitaires & Infos",
            value="• `/help` : Affiche ce menu d'aide.\n• `/ping` : Affiche la latence du bot.\n• `/userinfo [membre]` : Infos d'un utilisateur.\n• `/serverinfo` : Infos du serveur.\n• `/clear [nombre]` : Supprime des messages (max 100).",
            inline=False
        )
        embed.add_field(
            name="⚖️ Modération",
            value="• `/kick <membre> [raison]` : Expulse un membre.\n• `/ban <membre> [raison]` : Bannit un membre.\n• `/warn <membre> <raison>` : Avertit un membre.",
            inline=False
        )
        embed.add_field(
            name="🎮 Divertissement",
            value="• `/avatar [membre]` : Affiche l'avatar d'un membre.\n• `/roll [max]` : Lance un dé (max optionnel).\n• `/8ball <question>` : Pose une question à la Magic 8-Ball.",
            inline=False
        )
        embed.add_field(
            name="⚙️ Système",
            value="• `/stop` : Arrête proprement le bot (Admin/Owner uniquement).",
            inline=False
        )
        if client.user.avatar:
            embed.set_thumbnail(url=client.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="userinfo", description="Affiche les détails d'un utilisateur.")
    @app_commands.describe(member="Le membre dont vous souhaitez voir les informations")
    async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [role.mention for role in member.roles if role != interaction.guild.default_role]
        roles_str = " ".join(roles) if roles else "Aucun rôle"
        
        embed = discord.Embed(
            title=f"👤 Infos sur {member.name}",
            color=member.color if member.color.value != 0 else 0x3498DB
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
            
        embed.add_field(name="Nom d'utilisateur", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Bot ?", value="Oui" if member.bot else "Non", inline=True)
        
        created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S")
        joined_at = member.joined_at.strftime("%d/%m/%Y %H:%M:%S") if member.joined_at else "Inconnu"
        
        embed.add_field(name="Créé le", value=created_at, inline=False)
        embed.add_field(name="Rejoint le", value=joined_at, inline=False)
        embed.add_field(name=f"Rôles ({len(roles)})", value=roles_str, inline=False)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="serverinfo", description="Affiche les détails du serveur.")
    async def serverinfo(interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Cette commande ne peut être utilisée que dans un serveur.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title=f"🏰 Infos sur le serveur {guild.name}",
            color=0x3498DB
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="Propriétaire", value=guild.owner.mention if guild.owner else f"ID: {guild.owner_id}", inline=True)
        embed.add_field(name="ID du serveur", value=guild.id, inline=True)
        embed.add_field(name="Membres", value=guild.member_count, inline=True)
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles_count = len(guild.roles) - 1
        
        embed.add_field(name="Salons textuels", value=text_channels, inline=True)
        embed.add_field(name="Salons vocaux", value=voice_channels, inline=True)
        embed.add_field(name="Rôles", value=roles_count, inline=True)
        
        created_at = guild.created_at.strftime("%d/%m/%Y %H:%M:%S")
        embed.add_field(name="Créé le", value=created_at, inline=False)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="clear", description="Supprime un nombre défini de messages dans le salon.")
    @app_commands.describe(amount="Nombre de messages à supprimer (max 100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Veuillez spécifier un nombre entre 1 et 100.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 `{len(deleted)}` messages ont été supprimés.", ephemeral=True)

    @tree.command(name="kick", description="Expulse un membre du serveur.")
    @app_commands.describe(member="Le membre à expulser", reason="Raison de l'expulsion")
    @app_commands.default_permissions(kick_members=True)
    async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Vous ne pouvez pas expulser ce membre car il possède un rôle équivalent ou supérieur au vôtre.", ephemeral=True)
            return
        try:
            embed_dm = discord.Embed(
                title="🚪 Expulsion",
                description=f"Vous avez été expulsé du serveur **{interaction.guild.name}**.",
                color=0xE74C3C
            )
            embed_dm.add_field(name="Raison", value=reason)
            await member.send(embed=embed_dm)
        except Exception:
            pass
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Membre expulsé",
                description=f"**{member.name}** a été expulsé par **{interaction.user.name}**.",
                color=0x2ECC71
            )
            embed.add_field(name="Raison", value=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Impossible d'expulser ce membre : {e}", ephemeral=True)

    @tree.command(name="ban", description="Bannit un membre du serveur.")
    @app_commands.describe(member="Le membre à bannir", reason="Raison du bannissement")
    @app_commands.default_permissions(ban_members=True)
    async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Vous ne pouvez pas bannir ce membre car il possède un rôle équivalent ou supérieur au vôtre.", ephemeral=True)
            return
        try:
            embed_dm = discord.Embed(
                title="🔨 Bannissement",
                description=f"Vous avez été banni du serveur **{interaction.guild.name}**.",
                color=0xE74C3C
            )
            embed_dm.add_field(name="Raison", value=reason)
            await member.send(embed=embed_dm)
        except Exception:
            pass
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Membre banni",
                description=f"**{member.name}** a été banni par **{interaction.user.name}**.",
                color=0xE74C3C
            )
            embed.add_field(name="Raison", value=reason)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Impossible de bannir ce membre : {e}", ephemeral=True)

    @tree.command(name="warn", description="Donne un avertissement à un membre.")
    @app_commands.describe(member="Le membre à avertir", reason="Raison de l'avertissement")
    @app_commands.default_permissions(kick_members=True)
    async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
        try:
            embed_dm = discord.Embed(
                title="⚠️ Avertissement",
                description=f"Vous avez reçu un avertissement sur le serveur **{interaction.guild.name}**.",
                color=0xF1C40F
            )
            embed_dm.add_field(name="Raison", value=reason)
            embed_dm.add_field(name="Donné par", value=interaction.user.name)
            await member.send(embed=embed_dm)
            
            embed = discord.Embed(
                title="⚠️ Avertissement enregistré",
                description=f"**{member.name}** a reçu un avertissement.",
                color=0xF1C40F
            )
            embed.add_field(name="Raison", value=reason)
            embed.add_field(name="Modérateur", value=interaction.user.mention)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Impossible d'envoyer l'avertissement au membre : {e}", ephemeral=True)

    @tree.command(name="avatar", description="Affiche la photo de profil d'un membre.")
    @app_commands.describe(member="Le membre dont vous voulez voir l'avatar")
    async def avatar(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(
            title=f"🖼️ Avatar de {member.name}",
            color=0x3498DB
        )
        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="roll", description="Lance un dé aléatoire.")
    @app_commands.describe(max_val="La valeur maximale du dé (par défaut 100)")
    async def roll(interaction: discord.Interaction, max_val: int = 100):
        if max_val < 1:
            await interaction.response.send_message("La valeur maximale doit être supérieure à 0.", ephemeral=True)
            return
        result = random.randint(1, max_val)
        embed = discord.Embed(
            title="🎲 Lancement de Dé !",
            description=f"**{interaction.user.name}** a lancé un dé (1-{max_val}) et a obtenu :",
            color=0x9B59B6
        )
        embed.add_field(name="Résultat", value=f"🏆 **{result}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @tree.command(name="8ball", description="Pose une question à la Magic 8-Ball.")
    @app_commands.describe(question="Votre question à la boule magique")
    async def magic_8ball(interaction: discord.Interaction, question: str):
        responses = [
            "Essaye plus tard.", "Essaye encore.", "Pas d'avis.", "C'est ton destin.",
            "Le sort en est jeté.", "Une chance sur deux.", "Repose ta question.",
            "D'après moi oui.", "C'est certain.", "Oui absolument.", "Tu peux y compter.",
            "Sans aucun doute.", "Très probablement.", "Oui.", "C'est bien parti.",
            "C'est non.", "Peu probable.", "Faut pas y compter.", "Impossible.", "Ne compte pas là-dessus."
        ]
        response = random.choice(responses)
        embed = discord.Embed(
            title="🔮 Magic 8-Ball",
            color=0x2C3E50
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Réponse", value=f"🎱 **{response}**", inline=False)
        await interaction.response.send_message(embed=embed)

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
            f"Commandes  :  {MAGENTA}12 Commandes Slash actives{RESET}",
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
