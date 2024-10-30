# Minecraft Forge Server

This is a [Minecraft Forge server](https://files.minecraftforge.net/net/minecraftforge/forge/) that's running some mods
and hosted on [Fly.io](https://fly.io) for my friends. The repo has a couple uses that facilitate the server setup:

1. It lowers the likelihood of these files being lost if I accidentally delete or modify them in a way that 
2. It acts as a central repository for documentation (both as a user and as an admin)
3. It lets me automate the config and deployment with GitHub Actions

The crux of this setup comes from [Geoff Bourne's Minecraft Server Docker image](https://github.com/itzg/docker-minecraft-server), which is SUPER helpful for getting this up and running. If you're thinking of setting up your own server, I highly recommend using this!

# Connecting to the Server as a User

## General Server Info

- URL: gay-minecraft.fly.dev
- Minecraft version: 1.20.1
- Mod manager: Forge
- Forge version: 47.3.0

If you aren't allowed, message me your username to add you to the whitelist.

## Curseforge Instructions

1. Download the [modpack](https://github.com/jfreedman0212/mc-forge-server/releases/latest/download/client.zip)
2. In Curseforge, create a "new modpack", hit "Import", and select the zip file you just downloaded
3. If asked for the versions, enter the data in the [General Server Info section](#general-server-info)
4. Connect to the server!

## Manual Instructions

If you don't use Curseforge or some other mod manager, you'll need to do it manually. Also these instructions are
for Linux and Mac and assume some familiarity with the terminal.

1. Download Minecraft Java edition and run the launcher at least once (this creates the `~/.minecraft` folder)
2. Install the right version of Forge from [the website](https://files.minecraftforge.net/net/minecraftforge/forge/)
  - This downloads a JAR file, which you will run using `java -jar forge_installer.jar`. Worked using Java 11 for me, but YMMV.
3. Download the ["server" version of the modpack](https://github.com/jfreedman0212/mc-forge-server/releases/latest/download/server.zip)
  - Why the server version? Because it already has all the mod JAR files installed.
4. In your `~/.minecraft` folder, create a `mods` folder
5. Unzip the contents of the server modpack into the new `mods` folder
6. Run the Minecraft launcher as normal and select "Forge" from the dropdown
7. Connect to the server!

# Server Administration

## External Repository Configuration

There are 3 variables that get configured in GitHub for use in the Actions workflow:

- `FLY_API_TOKEN`: Fly.io API token for the gay-minecraft app
- `RELEASE_TOKEN`: GitHub personal access token
- `HAS_OVERRIDES_FOLDER`: set to `true` if the `modpack/overrides` folder exists, otherwise set to `false`

The first two are secrets since they're credentials for other systems. The last one is just a regular variable.

The `RELEASE_TOKEN` needs read-only "Metadata" permissions and read/write "Contents" permissions. **Just configure it
for this repo**, not all of them!

## Making Configuration Changes

All configuration (except for the datapacks, more on those later) are defined in this repository. If people are on the server 
and you want to make minor changes (like adding someone to the allowlist), you may do that through RCON commands. That way,
the server doesn't have to be restarted and affect your players. However, here's how to make longer lasting changes:

1. Make your changes in the repo:
  - `fly.toml` for general server config (this includes RCON commands for gamerules)
  - `ops.json` to change who the admins are
  - `whitelist.json` to change who's allowed to log into the server
  - `.github/workflows/release.yml` if you want to change the release process
2. [Make your commit, tag it, and push it](https://freedman.dev/tagging-a-commit-with-git/)
  - For some reason, I'm using semantic versioning but only updating the patch version?

That will kick off the Actions workflow and deploy the server. Check up on it to make sure it successfully
restarted. As of 10/30/2024, I've had to manually start it each release for some reason... TODO: fix that.

**Triggering a new release is critical for changes to take effect!** That's because the server looks for the _latest_
release for all the config files. You may delete old releases as they're no longer needed. It might be useful
to keep older versions of the modpacks around if those change.

## Adding Users to Allowlist or Ops

Get the person's username and enter it into [mcuuid.net](https://mcuuid.net/). I like to have both the username and the UUID
to be completely sure I'm only allowing my friends.

## Installing Datapacks

There's not an option in the Docker configuration (at least when I initially set it up in Summer 2023) to set up
datapacks from a zip file. So, I've manually installed them through SFTP. This doesn't require a server restart
in most cases. TODO: make this a more comprehensive, step-by-step guide
