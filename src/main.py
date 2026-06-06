
import discord
import os
import sys
from dotenv import load_dotenv

# Add directory to sys.path to allow proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import MyClient

# Styling constants
RED = "\033[91m"
RESET = "\033[0m"

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
