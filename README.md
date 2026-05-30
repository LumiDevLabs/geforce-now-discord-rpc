p align="center">
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

- **Cross-Platform:** Works on Windows and macOS.
- **Background Operation:** Runs quietly in the Windows system tray or macOS menu bar.
- **Auto-Detection:** Automatically detects whatever game you are playing on GeForce NOW.
- **Rich Status:** Updates your Discord profile with the game's actual name, cover art, and time played.
- **Easy Customization:** Edit settings right from a simple, friendly tray menu.
- **Auto-Start:** Optionally launch the app automatically when you log in.
- **Updates:** Automatically checks for new versions to keep things running smoothly.

---

## 🚀 Installation & Setup

### Step 1: GeForce NOW Setup
Before using this app, disable the built-in Discord Rich Presence in GeForce NOW so they do not conflict with each other:
1. Open **GeForce NOW**.
2. Go to **Settings** ⚙️ → **Connections**.
3. Scroll down to **Discord** and **disable** the toggle.

### Step 2: Download & Install GFN Discord RPC

#### 🪟 Windows
1. Download the latest installer (`GFNDiscordRPCSetup.exe`) from the [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases) page.
2. Run the installer and follow the instructions.
3. Once finished, look for the **🎮 icon** in your Windows system tray (bottom-right corner, near the clock).

#### 🍏 macOS
1. Download the `.dmg` file matching your Mac from the [Releases](https://github.com/LumiDevLabs/geforce-now-discord-rpc/releases) page:
   - **Apple Silicon (M1/M2/M3/M4/M5):** `GFN-Discord-RPC-arm64.dmg`
   - **Intel Macs:** `GFN-Discord-RPC-x86_64.dmg`
2. Open the `.dmg` and drag the **GFN Discord RPC** icon into your **Applications** folder.
3. Open the app from your Applications folder. Because the app is not code-signed, macOS will block it on the first launch. To bypass this:
   - **macOS 15 Sequoia and newer:** Double-click the app (you will see a warning — just close it). Go to your Mac's **System Settings** → **Privacy & Security**, scroll down to the **Security** section, and click **Open Anyway** next to the GFN Discord RPC message. Confirm and authenticate.
   - **macOS 14 Sonoma and older:** **Right-click** (or Control-click) the app in your Applications folder, select **Open**, and click **Open** again in the confirmation window.
4. The app runs directly in your **macOS menu bar** at the top right of your screen (it does not have a Dock icon).

> ℹ️ **Mac Screen Recording Permission:** On macOS, detecting what game is currently running requires reading the title of the GeForce NOW window. macOS protects window titles behind the "Screen Recording" permission. 
> 
> On your first run, macOS will ask for this permission. Go to **System Settings** → **Privacy & Security** → **Screen Recording**, enable **GFN Discord RPC**, and restart the app. **Note: No actual screen recording takes place.** The app only reads the title of the active window to know what game you are playing.

> 💡 **Troubleshooting Tip:** If macOS says the app is "damaged" and should be moved to the Trash, don't worry! This is a common macOS security quirk for unsigned apps. To fix it, open the **Terminal** app on your Mac, paste the following command, press **Enter**, and then try opening the app again:
> ```bash
> xattr -cr "/Applications/GFN Discord RPC.app"
> ```

---

## 🔑 One-Time Configuration (API Keys Setup)

To display game covers on Discord, the app needs three free API keys. This is a quick, one-time setup:

1. Launch the app. If keys are missing, it will automatically open a file named `secrets.json` for you. 
   *(You can also open this file at any time by right-clicking the app icon and selecting **Edit Secrets**).*
2. Fill in the keys using the guides below, save the file, and restart the app!

```json
{
    "GFN_DISCORD_CLIENT_ID": "your-discord-app-id",
    "GFN_STEAMGRIDDB_API_KEY": "your-steamgriddb-key",
    "GFN_IMGBB_API_KEY": "your-imgbb-key"
}
```

### How to get your keys:

#### 1. Discord Client ID (`GFN_DISCORD_CLIENT_ID`)
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and sign in.
2. Click **New Application** at the top right, name it (e.g., `GeForce NOW`), and click **Create**.
3. Under the **General Information** tab, find and copy the **Application ID** (a long number).
4. Paste it into your `secrets.json` as `GFN_DISCORD_CLIENT_ID`.
*(Note: No bots or complicated setup are required! Just make sure your desktop Discord application is open while playing.)*

#### 2. SteamGridDB API Key (`GFN_STEAMGRIDDB_API_KEY`)
*(This key is used to find beautiful cover images for the games you play.)*
1. Go to [SteamGridDB](https://www.steamgriddb.com/) and sign in using your Steam account.
2. Go to your preferences: [steamgriddb.com/profile/preferences](https://www.steamgriddb.com/profile/preferences)
3. Click the **API** tab and click **Request API Key** (or copy your existing one).
4. Paste it into your `secrets.json` as `GFN_STEAMGRIDDB_API_KEY`.

#### 3. ImgBB API Key (`GFN_IMGBB_API_KEY`)
*(This key is used to host game covers so Discord can load them in your status.)*
1. Go to [ImgBB API](https://api.imgbb.com/).
2. Sign up for a free account or log in.
3. Click **Add API Key** (or copy your existing key).
4. Paste it into your `secrets.json` as `GFN_IMGBB_API_KEY`.

---

## 🖱️ Using the App

Right-click the app's icon in your system tray (Windows) or menu bar (macOS) to control it:

- **`Edit Settings`** – Open configuration options (Windows opens a settings window; macOS opens the settings file).
- **`Edit Secrets`** – Quickly open the `secrets.json` file to update your API keys.
- **`Open Logs`** – Check the log file if something isn't working right.
- **`Check for Updates`** – Manually check if a new version is available.
- **`Start at Login`** – Toggle whether the app starts automatically when you turn on your computer.
- **`Quit` / `Close`** – Exit the app completely.

---

<details>
<summary>🛠️ Developer & Advanced Information (Expand to view)</summary>

### 📂 File Paths
If you need to access files directly, they are saved here:

**Windows:**
- Config: `%APPDATA%\GFN Discord RPC\config.json`
- Secrets: `%APPDATA%\GFN Discord RPC\secrets.json`
- Logs: `%APPDATA%\GFN Discord RPC\app.log`

**macOS:**
- Config: `~/Library/Application Support/GFN Discord RPC/config.json`
- Secrets: `~/Library/Application Support/GFN Discord RPC/secrets.json`
- Logs: `~/Library/Application Support/GFN Discord RPC/app.log`

### 🔨 Build from Source
Requires [Python 3.12+](https://www.python.org/) and [uv](https://github.com/astral-sh/uv).

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/LumiDevLabs/geforce-now-discord-rpc.git
   cd geforce-now-discord-rpc
   uv sync
   ```

2. Run the app directly:
   ```bash
   uv run python main.py
   ```

3. Build a standalone binary with [Nuitka](https://nuitka.net/):

   **Windows** (optionally builds an installer if [Inno Setup](https://jrsoftware.org/isinfo.php) is installed):
   ```powershell
   .\windows\build.ps1
   ```
   The compiled executable is placed in `dist\` and the installer in `installer\`.

   **macOS** (produces an `.app` bundle and a `.dmg` named by architecture):
   ```bash
   bash macos/build.sh
   ```
   The `.app` and `.dmg` are placed in `dist/`.

> ℹ️ Releases are built automatically by GitHub Actions (`.github/workflows/release.yml`): the Windows installer plus both Apple Silicon (`arm64`) and Intel (`x86_64`) macOS DMGs are published whenever a `v*` tag is pushed.

### 🗂️ Project Structure
```text
main.py            # entry point, dispatches on sys.platform
shared/            # cross-platform: config, constants, Discord RPC, artwork, updater, helpers
windows/           # Windows: tray, autostart (registry), game detection (Win32), build.ps1, installer.iss
macos/             # macOS: tray (menu bar), autostart (LaunchAgent), game detection (Quartz), build.sh
```

</details>
