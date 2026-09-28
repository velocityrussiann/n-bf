"""
Titles & Descriptions Parser - Neon Beats Factory (NBF)
Parses EDM titles/descriptions text file, matches songs by name or audio filename,
and generates viral high-CTR EDM metadata for unlisted tracks.
"""
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

CHANNEL_NAME = "Neon Beats Factory"
CHANNEL_TAG = "NBF"


def parse_titles_descriptions(filepath="titles_descriptions.txt"):
    """
    Parse the titles/descriptions text file.
    Returns a dict keyed by lowercase clean song title.
    """
    if not os.path.exists(filepath):
        print(f"[Parser] Notice: Titles file not found at '{filepath}'. Using automated viral metadata generator.")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    songs = {}
    sections = re.split(r'={40,}', content)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        title_match = re.search(r'TITLE:\s*(.+)', section)
        if not title_match:
            continue
        full_title = title_match.group(1).strip()

        desc_match = re.search(r'DESCRIPTION:\s*\n([\s\S]+)', section)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract core song name: part before " - " or " | "
        song_name = full_title
        for sep in [' - ', ' | ', ' — ']:
            if sep in song_name:
                song_name = song_name.split(sep)[0].strip()
                break

        clean_key = re.sub(r'[^a-z0-9]', '', song_name.lower())
        songs[clean_key] = {
            "title": full_title,
            "description": description,
            "song_name": song_name
        }

    print(f"[Parser] Parsed {len(songs)} EDM song entry(s) from {filepath}")
    return songs


def generate_viral_edm_metadata(audio_filename, channel_name="Neon Beats Factory"):
    """
    Generates high-CTR, high-SEO YouTube metadata specifically tailored
    for Electronic Dance Music (EDM) releases.
    """
    base = os.path.splitext(os.path.basename(audio_filename))[0].strip()
    # Remove leading numbering like '01 - ', 'LANDR-'
    clean_title = re.sub(r'^(LANDR[-\s_]+|\d+[\s\.\-_]+)', '', base, flags=re.IGNORECASE).strip()
    # Remove audio mastering suffixes
    clean_title = re.sub(r'[-_](Balanced|Open|Warm)[-_](Low|Medium|High)', '', clean_title, flags=re.IGNORECASE).strip()
    clean_title = clean_title.replace('_', ' ').replace('-', ' ').strip()
    clean_title = ' '.join(w.capitalize() for w in clean_title.split())
    if not clean_title:
        clean_title = "Neon Energy"

    viral_title = f"{clean_title} - {channel_name} (NBF) | Best Electronic Dance Music & Festival Drop"

    viral_description = f"""⚡ "{clean_title}" — {channel_name} (NBF)

Get ready for an unstoppable rush of festival energy. "{clean_title}" blends earth-shaking sub-bass, cutting-edge synthesizer sound design, and an infectious electronic groove that ignites dance floors and late-night drives.

🎧 Best experienced with high-end headphones or club sound systems!

🎵 Track Specifications:
• Track: {clean_title}
• Artist / Label: {channel_name} (NBF)
• Genre: Electronic Dance Music (EDM) / Electro House / Bass Drop
• Visualizer: 60 FPS Audio-Reactive 3D Core Visualizer
• Quality: 1080P Full HD / 320kbps Audio

⏱️ Track Chapters:
0:00 - Nocturnal Synth Atmosphere
0:25 - The Build & Tension
0:45 - Explosive Mainstage Bass Drop
1:30 - Harmonic Breakdown & Vocal Textures
1:55 - Peak Climax Drop
2:40 - Electric Horizon & Outro

🔥 Save to your EDM Playlist & Subscribe (🔔):
Join Neon Beats Factory for daily high-energy electronic music, cyberpunk soundscapes, and audio-reactive visualizers.

#EDM #ElectronicDanceMusic #NeonBeatsFactory #NBF #ElectroHouse #BassDrop #FestivalEDM #DanceMusic #ClubHits #60FPSVisualizer"""

    tags = [
        "edm",
        "electronic dance music",
        "neon beats factory",
        "nbf",
        clean_title.lower(),
        f"{clean_title.lower()} edm",
        "electro house",
        "bass drop",
        "festival music",
        "dance party mix",
        "club hits",
        "future house",
        "melodic edm",
        "60fps visualizer",
        "electronic music 2026"
    ]

    return {
        "title": viral_title,
        "description": viral_description,
        "song_name": clean_title,
        "tags": tags
    }


def get_song_metadata_by_name(audio_filename, filepath="titles_descriptions.txt"):
    """
    Looks up song metadata by filename with clean normalization.
    Falls back to generate_viral_edm_metadata if not found.
    """
    songs = parse_titles_descriptions(filepath)

    base = os.path.splitext(os.path.basename(audio_filename))[0].strip()
    clean_base = re.sub(r'^(LANDR[-\s_]+|\d+[\s\.\-_]+)', '', base, flags=re.IGNORECASE).strip()
    clean_base = re.sub(r'[-_](Balanced|Open|Warm)[-_](Low|Medium|High)', '', clean_base, flags=re.IGNORECASE).strip()
    norm_base = re.sub(r'[^a-z0-9]', '', clean_base.lower())

    # Direct match
    if norm_base in songs:
        meta = songs[norm_base]
        meta['tags'] = [
            "edm", "electronic dance music", "neon beats factory", "nbf",
            meta['song_name'].lower(), "electro house", "bass drop", "club hits"
        ]
        return meta

    # Substring / fuzzy match
    for key, data in songs.items():
        if key in norm_base or norm_base in key:
            data['tags'] = [
                "edm", "electronic dance music", "neon beats factory", "nbf",
                data['song_name'].lower(), "electro house", "bass drop", "club hits"
            ]
            return data

    # Fallback to automated EDM viral metadata
    print(f"[Parser] No explicit entry found for '{audio_filename}'. Generating viral EDM metadata...")
    return generate_viral_edm_metadata(audio_filename, channel_name=CHANNEL_NAME)


if __name__ == "__main__":
    test_files = [
        "Infinity New Mix.mp3",
        "All Night.mp3",
        "LANDR- Back to You-Balanced-Medium.wav",
        "Random Club Banger.mp3"
    ]
    for tf in test_files:
        meta = get_song_metadata_by_name(tf)
        print(f"\nTrack: {tf}")
        print(f"Title: {meta['title']}")
        print(f"Song Name: {meta['song_name']}")
        print(f"Desc Preview: {meta['description'][:100]}...")
