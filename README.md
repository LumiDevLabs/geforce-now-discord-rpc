<p align="center">
  <img width="256" height="256" alt="GFN Discord RPC" src="https://i.ibb.co/0RDZx9Jb/khgjghgh.webp" />
</p>

# 🎮 GFN Discord RPC

[![GitHub release](https://img.shields.io/github/v/release/LumiDevLabs/geforce-now-discord-rpc)](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue)](https://github.com/LumiDevLabs/geforce-now-discord-rpc)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?logo=discord&logoColor=white)](https://discord.com/developers/applications)
[![GeForce NOW](https://img.shields.io/badge/GeForce%20NOW-76b900?logo=nvidia&logoColor=white)](https://www.nvidia.com/en-us/geforce-now/)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Downloads](https://img.shields.io/github/downloads/LumiDevLabs/geforce-now-discord-rpc/total?logo=github&color=blue)](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases)

Show the game you are playing through NVIDIA GeForce NOW as Discord Rich Presence.

<img width="3128" height="1344" alt="GFN Discord RPC preview" src="https://i.ibb.co/k20rYk02/kjdusfhgvgjuszh.webp" />

***

## ✨ Features

- **Windows + macOS:** Runs in the Windows tray or macOS menu bar.
- **Auto Detection:** Finds the active GeForce NOW game automatically.
- **Rich Status:** Shows the game name, artwork, and play time on Discord.
- **Easy Settings:** Edit config, secrets, logs, updates, and auto-start from the app menu.
- **Update Checks:** Can check GitHub Releases for new versions.

## 🚀 Installation

Before using the app, open **GeForce NOW** → **Settings** → **Connections** and turn off GeForce NOW's built-in Discord Rich Presence so both apps do not fight each other.

### 🪟 Windows

1. Download `GFNDiscordRPCSetup.exe` from [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases).
2. Run the installer.
3. Start the app from the Windows tray icon.

### 🍏 macOS

1. Download the right `.dmg` from [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases):
   - Apple Silicon: `GFN-Discord-RPC-arm64.dmg`
   - Intel: `GFN-Discord-RPC-x86_64.dmg`
2. Open the `.dmg` and drag **GFN Discord RPC** into **Applications**.
3. Open the app. It lives in the macOS menu bar and has no Dock icon.

If macOS says the app is damaged, run this in Terminal and open it again:

```bash
sudo xattr -cr "/Applications/GFN Discord RPC.app"
```

On first launch, macOS may ask for **Screen Recording** permission. This is only used to read the GeForce NOW window title, not to record your screen. Enable it in **System Settings** → **Privacy & Security** → **Screen Recording**, then restart the app.

## ⚙️ First Setup

**No setup required.** The app uses a built-in Discord application and will show your game name with a default image right away. Just install and run.

All three keys below are **optional** — add them only if you want extra features.

<details>
<summary><b>Optional: Enable per-game artwork (SteamGridDB + ImgBB)</b></summary>

Without these keys the app shows a default GFN image for every game. Add both keys to fetch and display the actual game cover art.

**SteamGridDB API Key**

1. Sign in at [SteamGridDB](https://www.steamgriddb.com/).
2. Open [steamgriddb.com/profile/preferences](https://www.steamgriddb.com/profile/preferences).
3. Go to the **API** tab and copy/request your key.
4. Add it as `GFN_STEAMGRIDDB_API_KEY`.

**ImgBB API Key**

1. Open the [ImgBB API page](https://api.imgbb.com/).
2. Sign in or create an account.
3. Copy/create your API key.
4. Add it as `GFN_IMGBB_API_KEY`.

</details>

<details>
<summary><b>Optional: Use your own Discord application</b></summary>

By default the app registers your Discord status under the official GFN Discord RPC application. If you prefer your own Discord application name and icon, create one:

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Copy the **Application ID** from **General Information**.
4. Add it to `secrets.json` (see below) as `GFN_DISCORD_CLIENT_ID`.

No bot token or OAuth setup is needed.

</details>

### Adding optional keys

Open `secrets.json` via **Edit Secrets** in the tray/menu-bar menu and fill in only the keys you need, leave the rest as empty strings:

```json
{
    "GFN_DISCORD_CLIENT_ID": "",
    "GFN_STEAMGRIDDB_API_KEY": "",
    "GFN_IMGBB_API_KEY": ""
}
```

On Windows you can also add these as **user environment variables**: search for **environment variables**, open **Edit environment variables for your account**, and add each key under **User variables**.

## 🖱️ App Menu

Right-click the tray/menu bar icon to access:

- **`Edit Settings`** - Change app options.
- **`Open Config JSON`** - Open `config.json` directly (Windows only).
- **`Edit Secrets`** - Update API keys.
- **`Open Logs`** - Open the log file.
- **`Check for Updates`** - Check GitHub Releases manually.
- **`Start at Login`** - Toggle auto-start.
- **`Quit` / `Close`** - Exit the app.

## 📄 Files

Windows:

```text
%APPDATA%\GFN Discord RPC\
```

macOS:

```text
~/Library/Application Support/GFN Discord RPC/
```

This folder contains `config.json`, `app.log`, and `image_cache.json`. A `secrets.json` file is created the first time you use **Edit Secrets** (or you can create it manually).

## 🔨 Build from Source

Requires [Python 3.12+](https://www.python.org/) and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/LumiDevLabs/geforce-now-discord-rpc.git
cd geforce-now-discord-rpc
uv sync
uv run python main.py
```

Build Windows:

```powershell
.\windows\build.ps1
```

Build macOS:

```bash
bash macos/build.sh
```

Releases are built with GitHub Actions and include the Windows installer plus Apple Silicon and Intel macOS DMGs.
