<p align="center">
  <img width="256" height="256" alt="GFN Discord RPC" src="https://i.ibb.co/0RDZx9Jb/khgjghgh.webp" />
</p>

# 🎮 GFN Discord RPC

[![GitHub release](https://img.shields.io/github/v/release/LumiDevLabs/geforce-now-discord-rpc)](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-blue?logo=windows)](https://github.com/LumiDevLabs/geforce-now-discord-rpc)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?logo=discord&logoColor=white)](https://discord.com/developers/applications)
[![GeForce NOW](https://img.shields.io/badge/GeForce%20NOW-76b900?logo=nvidia&logoColor=white)](https://www.nvidia.com/en-us/geforce-now/)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Downloads](https://img.shields.io/github/downloads/LumiDevLabs/geforce-now-discord-rpc/total?logo=github&color=blue&cacheSeconds=300)](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases)

Show the game you are playing through NVIDIA GeForce NOW as Discord Rich Presence.

<img width="3128" height="1344" alt="GFN Discord RPC preview" src="https://i.ibb.co/k20rYk02/kjdusfhgvgjuszh.webp" />

***

## ✨ Features

- **Background Operation:** Runs quietly in the Windows system tray.
- **Auto-Detection:** Automatically detects the active GeForce NOW game window.
- **Rich Status:** Updates your Discord status with the game name and artwork.
- **Easy Configuration:** Edit settings directly from a simple tray menu.
- **Auto-Start:** Option to start automatically with Windows.
- **Update Checks:** Can automatically check GitHub Releases for new versions.

## 🚀 Installation

1. Download the latest installer from the [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases) page.
2. Run the installer setup. During installation, you can choose:
   - Where to install the application.
   - Whether it should start automatically when you sign in.
3. After installation, the app will appear in your **Windows system tray**.

## ⚙️ First Setup (~5 minutes)

Before using this app, disable the built-in Discord Rich Presence in GeForce NOW so it does not clash with this program:

1. Open **GeForce NOW**.
2. Go to **Settings** → **Connections**.
3. Scroll down and **disable** the default Discord Rich Presence option.

Then set the required **Windows environment variables** and configure the app from the tray menu.

### Required Environment Variables

1. Press **Win + S** and search **environment variables**.
2. Open **Edit environment variables for your account**.
3. Under **User variables**, click **New...**.
4. Use the variable name from the table below and paste the matching value into **Variable value**.
5. Repeat this for all three variables.
6. Click **OK** on every window, then fully close and reopen the app.

| Variable | Description |
| :--- | :--- |
| `GFN_DISCORD_CLIENT_ID` | Your Discord application client ID. |
| `GFN_STEAMGRIDDB_API_KEY` | Used to find game artwork from SteamGridDB. |
| `GFN_IMGBB_API_KEY` | Used to upload artwork so Discord can display it. |

> ℹ️ **Note:** These are Windows user environment variables, not entries in the config file. The app will show an error on startup if any are missing.

#### Discord Client ID (`GFN_DISCORD_CLIENT_ID`)

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and sign in.
2. Click **New Application**, choose a name (for example `GFN Discord RPC`), and click **Create**.
3. On **General Information**, copy the **Application ID**. This is the client ID used by Discord RPC.
4. Add it as the `GFN_DISCORD_CLIENT_ID` user environment variable.

> ℹ️ **Note:** Keep Discord desktop open while using this app. You only need the Application ID — no bot token or OAuth setup is required.

#### SteamGridDB API Key (`GFN_STEAMGRIDDB_API_KEY`)

1. Go to [SteamGridDB](https://www.steamgriddb.com/) and sign in with Steam.
2. Open your profile **Preferences** page: [steamgriddb.com/profile/preferences](https://www.steamgriddb.com/profile/preferences)
3. Open the **API** tab.
4. Copy your API key (or generate one if needed).
5. Add it as the `GFN_STEAMGRIDDB_API_KEY` user environment variable.

#### ImgBB API Key (`GFN_IMGBB_API_KEY`)

1. Open the [ImgBB API page](https://api.imgbb.com/).
2. Sign in or create an account if ImgBB asks you to.
3. Generate or copy your API key from the API page.
4. Add it as the `GFN_IMGBB_API_KEY` user environment variable.

> ℹ️ **Note:** ImgBB is free and hosts the game artwork so Discord can load it. Do not share your API key publicly.

Right-click the tray icon and select **`Edit Settings`** to configure the remaining options.

### Optional Settings

| Field | Description |
| :--- | :--- |
| `Check Interval Seconds` | How often the app checks the active game. |
| `Default Image URL` | Fallback image when no artwork is found. |
| `Activity Type` | Discord activity type (`PLAYING`, `LISTENING`, `WATCHING`, `COMPETING`). |
| `Check for Updates` | Checks for new GitHub Releases on startup. |

> ℹ️ **Note:** Settings are saved automatically to:
> `%APPDATA%\GFN Discord RPC\config.json`
> You do not need to edit anything inside the installation folder.

## 🖱️ Tray Menu

Right-click the tray icon to access all quick actions:

- **`Edit Settings`** – Open the settings window.
- **`Open Config JSON`** – Open the raw config file.
- **`Open Logs`** – Open the log file.
- **`Check for Updates`** – Check GitHub Releases manually.
- **`Start with Windows`** – Toggle auto-start.
- **`Close`** – Exit the app.

## 📄 Logs

Logs are stored here:

```text
%APPDATA%\GFN Discord RPC\app.log
```

## 🔨 Build from Source

Requires [Python 3.12+](https://www.python.org/) and [uv](https://github.com/astral-sh/uv).

1. Clone the repository and install dependencies:

```text
git clone https://github.com/LumiDevLabs/geforce-now-discord-rpc.git
cd geforce-now-discord-rpc
uv sync
```

2. Run the app directly:

```text
uv run python main.py
```

3. To build a standalone `.exe` and installer, run the build script (requires [Nuitka](https://nuitka.net/) and optionally [Inno Setup](https://jrsoftware.org/isinfo.php)):

```text
.\build.ps1
```

The compiled executable will be placed in `dist\` and the installer in `installer\`.
