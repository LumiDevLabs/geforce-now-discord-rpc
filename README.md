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

- **Cross-Platform:** Runs on both Windows and macOS.
- **Background Operation:** Runs quietly in the Windows system tray / macOS menu bar.
- **Auto-Detection:** Automatically detects the active GeForce NOW game window.
- **Rich Status:** Updates your Discord status with the game name and artwork.
- **Easy Configuration:** Edit settings directly from a simple tray menu.
- **Auto-Start:** Option to start automatically at login (Windows & macOS).
- **Update Checks:** Can automatically check GitHub Releases for new versions.

## 🚀 Installation

### Windows

1. Download the latest installer (`GFNDiscordRPCSetup.exe`) from the [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases) page.
2. Run the installer setup. During installation, you can choose:
   - Where to install the application.
   - Whether it should start automatically when you sign in.
3. After installation, the app will appear in your **Windows system tray**.

### macOS

1. Download the `.dmg` for your Mac from the [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases) page:
   - **Apple Silicon (M1/M2/M3/M4):** `GFN-Discord-RPC-arm64.dmg`
   - **Intel Macs:** `GFN-Discord-RPC-x86_64.dmg`
2. Open the `.dmg` and drag **GFN Discord RPC** into your **Applications** folder.
3. Because the app is not code-signed, macOS Gatekeeper will block it the first time. To open it:
   - **Right-click** (or Control-click) the app in Applications and choose **Open**, then click **Open** again in the dialog. You only need to do this once.
   - If you see "app is damaged", run this once in Terminal: `xattr -dr com.apple.quarantine "/Applications/GFN Discord RPC.app"`.
4. The app runs in the **macOS menu bar** (no Dock icon).

> ℹ️ **Screen Recording permission (macOS):** Game detection reads the GeForce NOW window title, which macOS protects behind the Screen Recording permission. On first run, grant it under **System Settings → Privacy & Security → Screen Recording**, enable **GFN Discord RPC**, then restart the app. No recording actually takes place; macOS simply gates window titles behind this permission.

## ⚙️ First Setup (~5 minutes)

Before using this app, disable the built-in Discord Rich Presence in GeForce NOW so it does not clash with this program:

1. Open **GeForce NOW**.
2. Go to **Settings** → **Connections**.
3. Scroll down and **disable** the default Discord Rich Presence option.

Then provide the three required **credentials** below and configure the app from the tray menu.

### Required Credentials

The app needs these three values:

| Key | Description |
| :--- | :--- |
| `GFN_DISCORD_CLIENT_ID` | Your Discord application client ID. |
| `GFN_STEAMGRIDDB_API_KEY` | Used to find game artwork from SteamGridDB. |
| `GFN_IMGBB_API_KEY` | Used to upload artwork so Discord can display it. |

There are two ways to supply them (the app checks environment variables first, then the secrets file):

**Option A — `secrets.json` (recommended, works on both platforms):**

1. Launch the app once. If credentials are missing, it creates and opens a `secrets.json` template for you.
2. You can also open it any time from the tray menu: **`Edit Secrets`**.
3. Fill in the three values and save, then restart the app. The file lives at:
   - **Windows:** `%APPDATA%\GFN Discord RPC\secrets.json`
   - **macOS:** `~/Library/Application Support/GFN Discord RPC/secrets.json`

```json
{
    "GFN_DISCORD_CLIENT_ID": "your-discord-app-id",
    "GFN_STEAMGRIDDB_API_KEY": "your-steamgriddb-key",
    "GFN_IMGBB_API_KEY": "your-imgbb-key"
}
```

**Option B — Environment variables:**

- **Windows:** Press **Win + S** → search **environment variables** → **Edit environment variables for your account** → add each key under **User variables**, then restart the app.
- **macOS:** Apps launched from Finder or at login **do not inherit** variables from your shell profile (`~/.zshrc`), so use **Option A** instead.

> ℹ️ **Note:** Keep your API keys private. The app shows an error on startup if any credential is missing from both sources.

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
> - **Windows:** `%APPDATA%\GFN Discord RPC\config.json`
> - **macOS:** `~/Library/Application Support/GFN Discord RPC/config.json`
>
> You do not need to edit anything inside the installation folder. On macOS, `Edit Settings` opens this JSON file in your default editor; the running app reloads it automatically when you save.

## 🖱️ Tray Menu

Right-click the tray icon to access all quick actions:

- **`Edit Settings`** – Open the settings (Windows: settings window; macOS: config JSON).
- **`Open Config JSON`** – Open the raw config file (Windows).
- **`Edit Secrets`** – Open `secrets.json` to set your credentials.
- **`Open Logs`** – Open the log file.
- **`Check for Updates`** – Check GitHub Releases manually.
- **`Start with Windows`** / **`Start at Login`** – Toggle auto-start.
- **`Close`** / **`Quit`** – Exit the app.

## 📄 Logs

Logs are stored here:

- **Windows:** `%APPDATA%\GFN Discord RPC\app.log`
- **macOS:** `~/Library/Application Support/GFN Discord RPC/app.log`

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

3. Build a standalone binary with [Nuitka](https://nuitka.net/):

   **Windows** (optionally builds an installer if [Inno Setup](https://jrsoftware.org/isinfo.php) is installed):

```text
.\windows\build.ps1
```

   The compiled executable is placed in `dist\` and the installer in `installer\`.

   **macOS** (produces an `.app` bundle and a `.dmg` named by architecture):

```text
bash macos/build.sh
```

   The `.app` and `.dmg` are placed in `dist/`.

> ℹ️ Releases are built automatically by GitHub Actions (`.github/workflows/release.yml`): the Windows installer plus both Apple Silicon (`arm64`) and Intel (`x86_64`) macOS DMGs are published whenever a `v*` tag is pushed.

## 🗂️ Project Structure

```text
main.py            # entry point, dispatches on sys.platform
shared/            # cross-platform: config, constants, Discord RPC, artwork, updater, helpers
windows/           # Windows: tray, autostart (registry), game detection (Win32), build.ps1, installer.iss
macos/             # macOS: tray (menu bar), autostart (LaunchAgent), game detection (Quartz), build.sh
```
