# Minecraft Forge Server

This is a [Minecraft Forge server](https://files.minecraftforge.net/net/minecraftforge/forge/) that's running some mods
and hosted on [Fly.io](https://fly.io) for my friends. The repo has a couple uses that facilitate the server setup:

1. It lowers the likelihood of these files being lost if I accidentally delete or modify them in a way that 
2. It acts as a central repository for documentation (both as a user and as an admin)
3. It lets me automate the config and deployment with GitHub Actions

The crux of this setup comes from [Geoff Bourne's Minecraft Server Docker image](https://github.com/itzg/docker-minecraft-server), which is SUPER helpful for getting this up and running. If you're thinking of setting up your own server, I highly recommend using this!

# Connecting to the server as a user

TODO:
- Installation of modpack from GitHub releases
- Importing in Curseforge
- Manually adding the mods to your `~/.minecraft` folder (if you can't use Curseforge)
- Connecting to the server (`gay-minecraft.fly.dev`)

# Server administration info

TODO:
- Installation of server modpack from GitHub releases
- Installation of datapacks to the world folder (manual/vanillatweaks)
- What to know to run it on Fly.io
    - Deploying new config changes
    - What requires a restart and what doesn't?
    - SSH'ing into the Fly Machine
    - Checking the logs/server metrics
- General MC Server administration
    - Adding users to the whitelist
    - Changing gamerules
    - Some other stuff???
