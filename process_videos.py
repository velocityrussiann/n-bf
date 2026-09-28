"""
Video Processor - Neon Beats Factory (NBF)
Orchestrates rendering of 60 FPS EDM videos and thumbnails using visualizer_core.py.
Configurable via environment variables.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

LOCAL_OUTPUT_DIR = os.getenv("LOCAL_OUTPUT_DIR", "Processed_Videos")
BG_DARKEN_FACTOR = float(os.getenv("BG_DARKEN_FACTOR", "0.50"))
VISUALIZER_COLOR = os.getenv("VISUALIZER_COLOR", "cyan")
VISUALIZER_DIAMETER = int(os.getenv("VISUALIZER_DIAMETER", "688"))
SHOW_SONG_TITLE = False  # Pure branding only (NBF logo + 3D core visualizer)


def process_single_song(image_path, audio_path, song_filename, display_name=None, force_rebuild=True, duration=None, recent_colors=None):
    """
    Renders video + matching thumbnail for a single song with 10-day anti-repetition color selection.
    """
    safe_name = os.path.splitext(song_filename)[0]
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_name:
        safe_name = "output"

    text_name = display_name if display_name else safe_name

    Path(LOCAL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    output_filename = f"{safe_name}.mp4"
    output_path = os.path.join(LOCAL_OUTPUT_DIR, output_filename)
    thumb_path = os.path.join(LOCAL_OUTPUT_DIR, f"{safe_name}_thumb.jpg")

    if os.path.exists(output_path) and not force_rebuild:
        print(f"[Processor] Skipping '{output_filename}' - already generated.")
        return output_path, thumb_path, {"label": "cached", "bgr": None}

    from visualizer_core import generate_nbf_video

    viz_candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Visualizer_Core_Only.viz"),
        "Visualizer_Core_Only.viz",
        r"D:\E agy cli\E bots\spynx\Visualizer_Core_Only.viz",
        r"C:\Users\kreg9\Downloads\Visualizer_Core_Only.viz",
    ]
    viz_path = next((p for p in viz_candidates if os.path.exists(p)), "Visualizer_Core_Only.viz")

    title_arg = text_name if SHOW_SONG_TITLE else None

    v_path, t_path, color_info = generate_nbf_video(
        viz_path=viz_path,
        bg_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
        fps=60,
        base_diameter=VISUALIZER_DIAMETER,
        color=VISUALIZER_COLOR,
        recent_colors=recent_colors,
        darken_factor=BG_DARKEN_FACTOR,
        song_title=title_arg,
        duration=duration
    )

    return v_path, t_path, color_info


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python process_videos.py <image_path> <audio_path> <song_name>")
        sys.exit(1)

    img = sys.argv[1]
    aud = sys.argv[2]
    name = sys.argv[3]
    dur = float(sys.argv[4]) if len(sys.argv) > 4 else None

    v, t = process_single_song(img, aud, name, display_name=name, duration=dur)
    print(f"\n[Processor] Complete:\n  Video: {v}\n  Thumbnail: {t}")
