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
|                                         : * = # # # # # # = * :             |
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
   - Clean, uncluttered design with zero extraneous text on canvas for a pure, professional brand presence.
3. **Audio-Reactive 3D Core Visualizer (Right Side)**:
   - Positioned at `X ~ 74.1%`, `Y ~ 48.5%` with a base diameter of `688px`.
   - Real-time STFT sub-bass analysis (25 Hz - 130 Hz) powering **BeatPulse**: drum kicks trigger dynamic mesh diameter expansion up to +18% with neon flash bloom.
   - Fluid 60 FPS continuous phase rotation synchronized to track tempo.
4. **10-Day Anti-Repetition Color Engine**:
   - Analyzes artwork in HSV space across multiple color clusters (Primary Dominant, Secondary Accent, and Complementary Opposite).
   - Tracks the last 10 published releases in `published_songs.json`.
   - Guaranteed: No two videos within a 10-day rolling window will ever share the same visualizer color, preventing amber/gold monotony and keeping your YouTube & Facebook video grid fresh, aesthetic, and diverse.
   - Expanded 12-color EDM neon palette: Electric Cyan, Radiant Amber/Gold, Cyber Magenta, Cobalt Blue, Toxic Lime, Molten Lava Fire, Ultraviolet, Laser Lemon, Hot Pink, Frosted Sky, Neo Mint, Crimson Flare.

---

## 🎵 AI Metadata, YouTube & Facebook Multi-Publishing

- **Pollinations AI Integration**: Generates viral, high-CTR EDM YouTube & Facebook video titles, 3-paragraph descriptions with track chapters, audio specs, and 15+ EDM tags via `https://gen.pollinations.ai/v1/chat/completions`. Automatically falls back to local curated EDM anthens if offline.
- **YouTube Playlist Automation**: Automatically searches or creates the official channel playlist:
  > *"Neon Beats Factory | Best Electronic Dance Music & EDM Hits"*
  and inserts every published release into it.
- **Facebook Page Video Publisher**: Automatically uploads high-resolution 60 FPS videos with custom thumbnails directly to the official Facebook Page:
  > **Neon Beats Factory** (Page ID: `538586562680121`) via Meta Graph API v21.0.

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
├── auto_pipeline.py                # Main orchestration pipeline (Fetch -> Render -> Multi-Publish -> Log)
├── process_videos.py               # Video processing interface with anti-repetition tracking
├── visualizer_core.py              # 60 FPS visualizer engine with darkening mask, branding & 10-day color logic
├── titles_descriptions_parser.py   # Pollinations AI metadata generator + local EDM fallback
├── titles_descriptions.txt         # Pre-configured viral EDM titles and descriptions
├── google_drive_fetch.py           # Google Drive downloader with local fallback & repost recycling
├── publish_youtube.py              # YouTube uploader with automatic playlist insertion
├── publish_facebook.py             # Facebook Page video publisher (Meta Graph API v21.0)
├── published_songs.json            # Deployment ledger tracking published songs & color history
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
  --image "C:\Users\kreg9\Downloads\Amsterdam_canals_at_night_20260929002216.jpg" \
  --audio "D:\NBF\AUDIO\Infinity New Mix.mp3" \
  --output "Processed_Videos/Amsterdam_Preview.mp4" \
  --darken 0.50 \
  --color variety
```

### 3. Run the Full Automation Pipeline

```bash
python auto_pipeline.py
```

Publishes automatically to both YouTube (with playlist insertion) and Facebook Page (`neonbeatsfactory`).

---

## ⚙️ GitHub Actions Automation

The repository is configured to publish automatically once per day via `.github/workflows/auto_publish.yml` using GitHub Secrets.

### Configured Secrets

| Secret Name | Description |
|---|---|
| `YT_CLIENT_ID` | Google Cloud Console OAuth 2.0 Client ID |
| `YT_CLIENT_SECRET` | Google Cloud Console OAuth 2.0 Client Secret |
| `YT_REFRESH_TOKEN` | OAuth 2.0 Refresh Token with YouTube Data API v3 scope |
| `FB_PAGE_ID` | Facebook Page ID (`538586562680121`) |
| `FB_PAGE_ACCESS_TOKEN` | Facebook Page Access Token for `neonbeatsfactory` |
| `POLLINATIONS_API_KEY` | Pollinations AI API key |
| `POLLINATIONS_ENDPOINT` | `https://gen.pollinations.ai/v1/chat/completions` |
| `GOOGLE_DRIVE_AUDIO_FOLDER_ID` | Google Drive folder ID containing your EDM audio files |
| `GOOGLE_DRIVE_IMAGE_FOLDER_ID` | Google Drive folder ID containing high-res background art |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Service Account JSON string with read access to the folders |

---

## 📜 License

MIT License. Designed with ⚡ by **Neon Beats Factory (NBF)**.
