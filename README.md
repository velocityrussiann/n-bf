# ⚡ Neon Beats Factory (NBF)

[![Auto Publish EDM Songs](https://github.com/velocityrussiann/n-bf/actions/workflows/auto_publish.yml/badge.svg)](https://github.com/velocityrussiann/n-bf/actions/workflows/auto_publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-brightgreen.svg)](https://python.org)
[![Visualizer: 60FPS](https://img.shields.io/badge/Visualizer-60%20FPS-00f0ff.svg)](#)

**Neon Beats Factory (NBF)** is an automated YouTube publishing bot and high-performance 60 FPS music video generator built specifically for **Electronic Dance Music (EDM)**.

Inspired by [`velocitykorean/spynx`](https://github.com/velocitykorean/spynx), NBF is designed for nocturnal, high-energy festival and club releases with automated background darkening masks, iconic brand overlays, real-time sub-bass beat pulsing, and automated YouTube playlist management.

---

## 🎨 Visual Identity & Layout

Every video and thumbnail is rendered in standard **1080P Full HD (1920x1080)** at **60 FPS** with zero seek drift:

```
+-----------------------------------------------------------------------------+
|                                                                             |
|                                                                             |
|     +-------------+                        . : * = # # = * : .              |
|     |     NBF     |                     : * = # # # # # # = * :             |
|     |  NEON BEATS |                    * = # # # # # # # # # = *            |
|     |   FACTORY   |                   = # # # # # # # # # # # # =           |
|     +-------------+                   = # # # # # # # # # # # # =           |
|                                        * = # # # # # # # # # = *            |
|  NOW PLAYING: INFINITY (NEW MIX)        : * = # # # # # # = * :             |
|                                            . : * = # # = * : .              |
|                                                                             |
+-----------------------------------------------------------------------------+
```

1. **Intelligent Darkening Mask**:
   Background artwork (such as bright city skylines or day photos) is automatically processed through a calibrated darkening filter (`BG_DARKEN_FACTOR=0.50`) and smooth radial vignette falloff. This guarantees high contrast and ensures the glowing cyan visualizer and white branding never get washed out.
2. **Iconic NBF Branding (Left Side)**:
   - Centered vertically at `X ~ 22%`, `Y ~ 48.5%`.
   - Sharp, solid white geometric typography featuring the distinctive sliced `N`, bold rounded `B`, and cut `F`.
   - Pill card with `NEON BEATS FACTORY` and smooth drop-shadow.
   - Clean song title card (`NOW PLAYING: <SONG NAME>`) positioned directly below the logo.
3. **Audio-Reactive 3D Core Visualizer (Right Side)**:
   - Positioned at `X ~ 74.1%`, `Y ~ 48.5%` with a base diameter of `688px`.
   - Real-time STFT sub-bass analysis (25 Hz - 130 Hz) powering **BeatPulse**: drum kicks trigger dynamic mesh diameter expansion up to +18% with neon flash bloom.
   - Fluid 60 FPS continuous phase rotation synchronized to track tempo.
   - Electric Cyan / Aqua (`#8DFCFE`) multi-stage neon glow.

---

## 🎵 Electronic Dance Music (EDM) SEO & Playlists

- **Viral Title & Description Generator**: Pre-loaded with high-CTR, SEO-optimized metadata for festival drops, electro house, slap house, cyberpunk beats, and melodic EDM.
- **YouTube Playlist Automation**: Automatically searches for the official channel playlist:
  > *"Neon Beats Factory | Best Electronic Dance Music & EDM Hits"*
  If not found, it automatically creates the playlist via YouTube Data API and inserts every published release into it.

---

## 📁 Repository Structure

```
n-bf/
├── .github/
│   └── workflows/
│       └── auto_publish.yml        # Daily GitHub Actions cron automation
├── assets/
│   └── nbf_logo.png                # Official transparent NBF branding asset
├── fonts/
│   ├── Montserrat-Bold.ttf
│   ├── Outfit-Bold.ttf
│   └── BebasNeue-Regular.ttf
├── input_audio/                    # Local folder for offline test tracks
├── input_images/                   # Local folder for offline test backgrounds
├── auto_pipeline.py                # Main orchestration pipeline (Fetch -> Render -> Upload -> Log)
├── process_videos.py               # Video processing interface
├── visualizer_core.py              # 60 FPS visualizer engine with darkening mask & NBF branding
├── titles_descriptions_parser.py   # EDM SEO title & description parser + fallback generator
├── titles_descriptions.txt         # Pre-configured viral EDM titles and descriptions
├── google_drive_fetch.py           # Google Drive downloader with local fallback
├── publish_youtube.py              # YouTube uploader with automatic playlist insertion
├── published_songs.json            # Deployment ledger preventing duplicate uploads
├── Visualizer_Core_Only.viz        # 3D topographic Avee visualizer core
├── requirements.txt                # Python dependencies
├── .env.example                    # Configuration template
└── README.md
```

---

## 🚀 Quick Start (Local Usage)

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/velocityrussiann/n-bf.git
cd n-bf
pip install -r requirements.txt
```

*Ensure FFmpeg is installed and accessible in your system `PATH`.*

### 2. Render a Video Locally

You can test video and thumbnail generation on any audio + image pair:

```bash
python visualizer_core.py \
  --image "C:\Users\kreg9\Downloads\Istanbul_skyline_at_night_20260928054559.jpg" \
  --audio "D:\NBF\AUDIO\Infinity New Mix.mp3" \
  --output "Processed_Videos/Infinity_Preview.mp4" \
  --title "Infinity (New Mix)" \
  --darken 0.50 \
  --color cyan
```

### 3. Run the Full Automation Pipeline

```bash
python auto_pipeline.py
```

If Google Drive credentials are not supplied, the pipeline automatically checks local folders (`input_audio/` and `input_images/` or `D:\NBF\AUDIO` and `D:\NBF\Cover Art`).

---

## ⚙️ GitHub Actions Automation

The repository is configured to publish automatically once per day via `.github/workflows/auto_publish.yml` using GitHub Secrets.

### Required Secrets

Go to **Repository Settings → Secrets and variables → Actions** and add:

| Secret Name | Description |
|---|---|
| `GOOGLE_DRIVE_AUDIO_FOLDER_ID` | Google Drive folder ID containing your EDM audio files |
| `GOOGLE_DRIVE_IMAGE_FOLDER_ID` | Google Drive folder ID containing high-res background art |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Service Account JSON string with read access to the folders |
| `YT_CLIENT_ID` | Google Cloud Console OAuth 2.0 Client ID |
| `YT_CLIENT_SECRET` | Google Cloud Console OAuth 2.0 Client Secret |
| `YT_REFRESH_TOKEN` | OAuth 2.0 Refresh Token with YouTube Data API v3 scope |

---

## 📜 License

MIT License. Designed with ⚡ by **Neon Beats Factory (NBF)**.
