# AFK VOC HOST RENDER

Ce projet a pour but de garder un compte Discord dans un salon vocal.

## Fonctionnalités

- Connexion automatique au vocal
- Reconnexion en cas d’expulsion
- Serveur Flask pour hébergement sur Render.com

## Installation

1. Installez les fichiers du projet en les ajoutant un par un dans un repository GitHub.
2. Assurez-vous que tous les fichiers nécessaires (comme `start.py`, `requirements.txt`.) sont présents.

## Déploiement sur Render.com

1. Rendez-vous sur [Render.com](https://render.com) et connectez-vous en vous inscrivant via GitHub.
2. Cliquez sur **Web Service** puis sélectionnez le repository que vous avez créé sur GitHub.
3. Configurez les variables d'environnement dans Render :

   - `USERTOKEN` : le token utilisateur Discord
   - `GUILD_ID` : l'ID du serveur où vous souhaitez que le compte soit en mode vocal AFK
   - `CHANNEL_ID` : l'ID du salon vocal où le compte se connectera

4. Dans le champ **Start Command**, entrez :

python start.py

Déployez votre service.

## Rester en ligne 24/7

Pour que votre service reste actif en permanence, utilisez [Uptime Robot](https://uptimerobot.com/).  
Configurez-le pour envoyer régulièrement des requêtes HTTP à votre URL Render.  
Cela permet que votre service soit en fonctionnement continu.

⚠️ Attention : Ce script utilise un token utilisateur, ce qui est contre les règles de Discord. L'utilisation de ce script peut entraîner le bannissement de votre compte Discord. Utilisez-le à vos risques et périls.
