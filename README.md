# ModBot [WIP]

## A discord bot for basic moderation

## Setup  
#### Dependencies
| Name| installation instructions | 
| ------------- | -------------------------------------------------------- |  
| A Discord bot |  https://discordpy.readthedocs.io/en/latest/discord.html |
| Docker |  https://docs.docker.com/engine/install/ |
| Docker-compose =< 1.27 |  https://docs.docker.com/compose/install/ | 
 
### Installation instructions
#### Make sure you put your own secrets into the config files before you build the container
```
$ git clone https://github.com/NetworkChuckDiscord/Modmail.git && cd Modmail
$ nano .mongoenv.sample # set the mongodb password here
$ cp .mongoenv.sample .mongoenv
$ nano defaults.py # set default settings in here see chart below for descriptions
$ nano .discordenv.sample # set your discord-token and use the same password as set earlier
$ cp .discordenv.sample .mongoenv
$ docker build . -t modmail
$ docker compose up -d
```
