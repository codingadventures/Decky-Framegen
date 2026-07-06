# Decky Framegen Plugin

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B71HZTAX)

A Steam Deck plugin that enables DLSS upscaling and Frame Generation on handhelds by utilizing the latest OptiScaler and supporting modification software. This plugin automatically installs and manages all necessary components for FSR-based frame generation in games that support DLSS, or OptiFG for adding FG to games that do not have any existing FG pathway (highly experimental)

## What This Plugin Does

This plugin uses OptiScaler to replace DLSS calls with FSR3/FSR3.1, giving you:

- **Frame Generation**: Smooth out your frame rate using AMD's FSR3 pathways
- **Upscaling**: Improves performance while maintaining visual quality using FSR and XESS using DLSS FSR or XESS inputs. Upgrade FSR 2 games to FSR 3.1.4 or XESS for better visual quality.
- **Easy Management**: One-click installation and game patching/unpatching through the Steam Deck interface. No going into desktop mode every time you want to add or remove OptiScaler from a game!

## Features

### Core Functionality
- **One-Click Setup**: Automatically downloads and installs OptiScaler into a "fgmod" directory
- **Smart Installation**: Handles all required dependencies and library files
- **Game Patching**: Easy copy-paste launch commands for enabling/disabling the mod per game
- **GPU-Aware Defaults**: Detects your GPU and recommends the matching FSR4 runtime (RDNA4 native vs the RDNA2/3/3.5 INT8 override)
- **Compatibility Marking**: Flags which installed games are OptiScaler compatible, with independent **Verified** / **Compatible** filters and a per-game manual override
- **OptiScaler Wiki**: Direct access to OptiScaler documentation and settings via a webpage launch button right inside the plugin.

### Supported Devices

This is a Decky Loader plugin, so it works on any handheld/PC running SteamOS (or a compatible distro like Bazzite) with Decky Loader installed. Tested targets include the Steam Deck (LCD/OLED) and it also runs on other AMD handhelds such as the Lenovo Legion Go / Legion Go 2 (RDNA3 / RDNA3.5) and ROG Ally.

On launch the plugin detects your GPU and pre-selects a sensible **Default FSR4 runtime**:
- **RDNA4** (e.g. Radeon RX 9000 series) -> native FSR4 runtime
- **RDNA2 / RDNA3 / RDNA3.5** (Steam Deck, Legion Go / Go 2, ROG Ally, etc.) -> the bundled INT8 override
- **Unknown / non-AMD** -> safe INT8 default

You can always override the runtime manually from the "Default FSR4 runtime" dropdown.

### Which Games Are Compatible?

OptiScaler works by hooking a game's existing upscaler, so it mainly benefits titles that already expose **DLSS 2+, FSR2+, or XeSS** (games with no upscaler at all only have the experimental OptiFG path). The plugin marks each installed game as:
- **Verified**: the game appears on the community [OptiScaler compatibility list](https://github.com/optiscaler/OptiScaler/wiki/Compatibility-List) by name - the strongest signal, since it reflects real community testing (also covers games that statically link FSR and have no detectable DLL).
- **Compatible**: an upscaler DLL (`nvngx_dlss.dll`, `libxess.dll`, FSR FidelityFX libraries) was found in the game folder - a good heuristic, but not community-verified.
- **Unknown**: no signal either way. Not shown as a badge in the game list to keep it readable; visible in the compatibility detail field for the selected game.
- **Not compatible**: you manually marked it as such via the override. Also hidden from the list/badges.

Only games that are actually installed on disk are listed (Steam's leftover `appmanifest` entries for removed games are skipped). Manually marking a game **Compatible** or **Not compatible** always takes priority over the automatic detection. Use the **Filter: Verified** and **Filter: Compatible** toggles to narrow the game dropdown (with neither enabled, every installed game is shown), and the **Compatibility override** dropdown to force a per-game result.

Detection is best-effort and cached. The curated list is fetched over a verified TLS connection (using the system CA bundle) at most once a day; a snapshot of the list also **ships with the plugin**, so Verified marking keeps working offline or when GitHub rate-limits the request (HTTP 429). If the live list can't be fetched, the plugin transparently falls back to the bundled snapshot and the filter description notes it. Even with no curated list at all, games can still be marked **Compatible** by the local DLL scan.

> **Note:** The game list and compatibility marking cover your **Steam library** only (they read Steam's `appmanifest` files). Games installed through Heroic (Epic/GOG/Amazon) or Lutris won't appear in the dropdown, but you can still patch them manually with the `~/fgmod/fgmod %command%` wrapper (the launcher script includes Lutris resolution).

> **Heads up on frame generation:** OptiScaler already provides frame generation. Don't stack it with another frame-gen solution such as Lossless Scaling / `lsfg-vk` at the same time - two frame-gen layers compound latency and artifacts. Pick one for frame generation.

## How to Use

1. **Install the Plugin**: Download and install through Decky Loader "install from zip" option in developer settings
2. **Setup OptiScaler**: Open the plugin and click "Setup OptiScaler Mod" 
3. **Configure Games**: For each game you want to enhance:
   - Click "Copy launch options" in the plugin for the standard direct launch-options method
   - Go to your game's Properties → Launch Options in Steam
   - Paste the copied command
   - If you want the wrapper commands instead, enable Manual Mode and use "Copy Patch Command" / "Copy Unpatch Command"
4. **Enable Features**: Launch your game and enable DLSS in the graphics settings
5. **Advanced Options**: Press the Insert key in-game for additional OptiScaler settings

### Removing the Mod from Games
- If you used the wrapper method, enable Manual Mode and click "Copy Unpatch Command", then replace the launch options with: `~/fgmod/fgmod-uninstaller.sh %command%`
- If you used the standard direct patch flow, use the in-plugin unpatch button instead
- Run the game at least once to make the uninstaller script run. After that you can leave the launch option or remove it

### Configuring OptiScaler via Environment Variables
As of v0.15.1, you can update OptiScaler settings before a game launches by adding environment variables. 
This is useful if you plan to use the same settings across multiple games so they are pre-configured by the time you launch them.

For example, considering the following sample from the OptiScaler.ini config file:
```
[Upscalers]
Dx11Upscaler=auto
Dx12Upscaler=auto
VulkanUpscaler=auto

[FrameGen]
Enabled=auto
FGInput=auto
FGOutput=auto
DebugView=auto
DrawUIOverFG=auto
```
We can decide to set `Dx12Upscaler=fsr31` to enable FSR4 in DX12 games by default. This works because the option name `Dx12Upscaler` is unique throughout the file but for options that appear multiple times like `Enabled`, you can prefix the option name with the section name like `FrameGen_Enabled=true`.
You can provide section names for all options if you want to be explicit. You can also prefix `Section_Option` with `OptiScaler` to ensure no conflict with other commands.

Here's the breakdown of supported formats:
- `OptiScaler_Section_Option=value` - Full format (foolproof)
- `Section_Option=value` - Short format (recommended)
- `Option=value` - Minimal format (only works if the option name appears once in OptiScaler.ini)

**Example:**
```bash
# Enable frame generation with XeFG output
FrameGen_Enabled=true FGInput=fsrfg FGOutput=xefg ~/fgmod/fgmod %command%

# Set DX12 upscaler to FSR 3.1 (Upgrades to FSR4)
Dx12Upscaler=fsr31 ~/fgmod/fgmod %command%
```

**Notes:**
- Environment variables override the OptiScaler.ini file on each game launch
- Hyphenated section names like `[V-Sync]` can be accessed like `VSync_Option=value`
- If an option name appears in multiple sections of the OptiScaler.ini file, use the `Section_Option` or `OptiScaler_Section_Option` format

## Technical Details

### What's Included
- **[OptiScaler 0.9.3](https://github.com/optiscaler/OptiScaler/releases/tag/v0.9.3)**: Official upstream OptiScaler bundle used by this plugin, with bundled FSR4 runtime variants for the archive-native RDNA4 path, the Steam Deck / RDNA2-3 optimized INT8 override, or the official 4.1.1 RDNA 3/4 override
- **Nukem9's DLSSG to FSR3 mod**: Allows use of DLSS inputs for FSR frame gen outputs, and xess or FSR upscaling outputs
- **FakeNVAPI**: NVIDIA API emulation for AMD/Intel GPUs, to make DLSS options selectable in game
- **Supporting Libraries**: All required DX12/Vulkan libraries (libxess.dll, amd_fidelityfx, etc.)


## Building From Source

This plugin is built with the [Decky CLI](https://github.com/SteamDeckHomebrew/cli), which runs the frontend `rollup` build, downloads the bundled `remote_binary` assets (OptiScaler archive + FSR4 DLLs) declared in `package.json`, and packages everything into an installable zip.

### In CI (recommended)

A GitHub Actions workflow at [.github/workflows/build.yml](.github/workflows/build.yml) builds the plugin on every push/PR and uploads the zip as a build artifact. Pushing a `v*` tag additionally publishes a GitHub Release with the zip attached:

```bash
git tag v0.16.0
git push origin v0.16.0
```

### Locally

Requires Docker (the CLI builds inside a Linux container) and the Decky CLI binary in `./cli/decky`:

```bash
# One-time: fetch dependencies + the Decky CLI (interactive)
.vscode/setup.sh

# Build -> produces out/<plugin-name>.zip
just build        # or: .vscode/build.sh
```

Then install the resulting zip via Decky Loader's "Install from ZIP" option in developer settings. Note: a full build cannot run on machines without Docker (e.g. stock macOS without Docker Desktop) - use the CI workflow instead.

### Unit tests

Compatibility parsing/classification logic lives in [`compat_logic.py`](compat_logic.py) and is tested against a real snapshot of the OptiScaler wiki list in [`tests/fixtures/Compatibility-List.md`](tests/fixtures/Compatibility-List.md):

```bash
python3 -m unittest discover -s tests -v
# or
just test
```

Refresh the fixture when the wiki list changes materially (see [`tests/fixtures/README.md`](tests/fixtures/README.md)).

## Debugging on a running device

Yes — the plugin logs via `decky.logger` to a **file only** (not your screen/TTY in Game Mode). You can tail that file over SSH while using the plugin on your Deck / Legion Go.

### Verbose debug logging toggle

By default the plugin only writes high-signal lines (`info`/`warning`/`error`): install/patch success, failures, etc.

Enable **Verbose debug logging** at the bottom of the plugin UI to also record detailed diagnostics (`debug` level), including:

- GPU detection details
- Compatibility scan summaries (`compat summary: verified=...`)
- Per-file patch/unpatch steps
- Curated list fetch/SSL retry details

The setting is stored under `~/homebrew/settings/Decky-Framegen/debug-logging.json` and takes effect immediately (no plugin reload required).

### Plugin log (Python backend + frontend errors)

Decky writes plugin logs under your homebrew folder. For this plugin the main file is typically:

```text
~/homebrew/logs/Decky-Framegen/plugin.log
```

Tail it live over SSH (replace user/host as needed):

```bash
ssh deck@YOUR_DEVICE 'tail -f ~/homebrew/logs/Decky-Framegen/plugin.log'
```

Useful lines to grep for:

```bash
ssh deck@YOUR_DEVICE "grep '\\[Framegen\\]' ~/homebrew/logs/Decky-Framegen/plugin.log | tail -50"
```

What you'll see (with **Verbose debug logging** enabled):

- `[Framegen] detect_gpu: ...` — GPU detection + recommended FSR4 variant
- `[Framegen] compat summary: verified=... compatible=... curated_error=...` — result of the compatibility scan
- `[Framegen] curated compat fetch failed: ...` or TLS retry warnings — explains why everything looked "Unknown"
- `[Framegen] patch_game / unpatch_game ...` — per-game patch actions (detailed target lines are debug-only)
- `FRONTEND: ...` — errors forwarded from the React UI via `logError()`

With verbose logging **off**, you still get patch/unpatch success lines and all warnings/errors.

Decky Loader itself also logs to `journalctl`; if the plugin log is empty, check:

```bash
ssh deck@YOUR_DEVICE 'journalctl -u plugin_loader -f'
```

### fgmod launcher logs (when a game starts)

If you patch via `~/fgmod/fgmod %command%`, the wrapper also logs to the system journal and a temp file:

```bash
ssh deck@YOUR_DEVICE 'journalctl -t fgmod -f'
ssh deck@YOUR_DEVICE 'tail -f /tmp/fgmod-install.log'
```

### Cached compatibility data on device

After a scan, inspect what the plugin stored locally:

```bash
ssh deck@YOUR_DEVICE 'ls -la ~/fgmod/compat-*'
ssh deck@YOUR_DEVICE 'python3 -m json.tool ~/fgmod/compat-curated-cache.json | head'
```

## Credits

### Core Technologies
- **[Nukem9](https://github.com/Nukem9/dlssg-to-fsr3)** - Creator of the DLSS to FSR3 mod that makes frame generation possible
- **[Cdozdil/OptiScaler Team](https://github.com/optiscaler/OptiScaler)** - OptiScaler mod that provides the core functionality and bleeding-edge improvements
- **[Artur Graniszewski](https://github.com/artur-graniszewski/DLSS-Enabler)** - DLSS Enabler that allows DLSS features on non-RTX hardware
- **[FakeMichau](https://github.com/FakeMichau)** - Various essential tools including fgmod scripts, innoextract, and fakenvapi for AMD/Intel GPU support

### Community & Documentation
- **[Deck Wizard](https://www.youtube.com/watch?v=o_TkF-Eiq3M)** - Extensive community support including comprehensive guides, promotional content, thorough testing and feedback, custom artworks, and tutorial videos. His passionate advocacy and continuous support have been instrumental in Decky Framegen's success.

- **The DLSS2FSR Community** - Ongoing support and guidance for understanding the various mods and tools
