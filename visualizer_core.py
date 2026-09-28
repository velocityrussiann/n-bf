"""
Neon Beats Factory (NBF) - High-Performance 60 FPS Audio-Reactive Visualizer Engine
Generates viral Electronic Dance Music (EDM) videos and matching thumbnails:
1. Intelligent Background Darkening Mask & Cinematic Vignette (prevents neon washout)
2. Iconic NBF (NEON BEATS FACTORY) Branding on Left Side
3. 3D Topographic Mesh Core Visualizer with Sub-Bass BeatPulse on Right Side
4. Multi-Stage Neon Cyan Glow & Dynamic Bloom
5. Sample-accurate 0.0ms Audio Sync
6. High-Impact Matching YouTube Thumbnail Generation
"""

import os
import sys
import re
import time
import zipfile
import subprocess
import tempfile
import numpy as np
import cv2
import soundfile as sf
import scipy.signal
from PIL import Image, ImageSequence, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Color palettes (BGR)
NEON_PALETTE = {
    "cyan": (250, 240, 60),        # Electric Cyan / Aqua (Screenshot Default)
    "ice_blue": (255, 225, 140),   # Frosted Sky Cyan
    "gold": (70, 215, 255),        # Radiant Golden Fire
    "yellow": (70, 235, 255),      # Neon Lemon
    "pink": (210, 140, 255),       # Cyber Neon Rose
    "magenta": (255, 60, 220),     # Electric Magenta
    "purple": (255, 130, 180),     # Neon Violet
    "green": (80, 255, 120),       # Toxic Lime Green
    "white": (255, 255, 255),      # Pure Diamond White
}


def load_viz_core(viz_path, color_bgr=(250, 240, 60)):
    """
    Extracts mesh_core.gif from Visualizer_Core_Only.viz and pre-tints frames with neon glow.
    """
    print(f"[NBF Visualizer] Extracting core from: {viz_path}", flush=True)
    with zipfile.ZipFile(viz_path, 'r') as z:
        names = z.namelist()
        if "mesh_core.gif" in names:
            gif_bytes = z.read("mesh_core.gif")
        elif "1089483" in names:
            gif_bytes = z.read("1089483")
        else:
            largest = max(z.infolist(), key=lambda x: x.file_size)
            gif_bytes = z.read(largest.filename)

    import io
    gif_file = io.BytesIO(gif_bytes)
    im = Image.open(gif_file)

    pil_frames = [f.copy().convert("RGBA") for f in ImageSequence.Iterator(im)]
    num_frames = len(pil_frames)
    print(f"[NBF Visualizer] Loaded {num_frames} animation frames from .viz core.", flush=True)

    tinted_frames = []
    cb, cg, cr = color_bgr

    for frame in pil_frames:
        arr = np.array(frame)
        alpha = arr[:, :, 3]
        gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGBA2GRAY).astype(np.float32) / 255.0

        tinted = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.float32)
        tinted[:, :, 0] = gray * cb
        tinted[:, :, 1] = gray * cg
        tinted[:, :, 2] = gray * cr

        alpha_mask = (alpha.astype(np.float32) / 255.0)[:, :, np.newaxis]
        tinted_alpha = tinted * alpha_mask

        # Multi-stage neon bloom
        b1 = cv2.GaussianBlur(tinted_alpha, (11, 11), 0)
        b2 = cv2.GaussianBlur(tinted_alpha, (29, 29), 0)
        glowing = np.clip(tinted_alpha * 1.25 + b1 * 0.75 + b2 * 0.40, 0, 255).astype(np.uint8)

        tinted_frames.append(glowing)

    return tinted_frames


def apply_darkening_mask(bg_bgr, darken_factor=0.50, vignette_intensity=0.25):
    """
    Applies cinematic darkening mask & vignette to prevent bright backgrounds
    from drowning out the neon visualizer and white branding.
    """
    H, W = bg_bgr.shape[:2]

    # 1. Base Darkening Multiplier (0.50 = 50% luminance of original)
    darkened = (bg_bgr.astype(np.float32) * darken_factor).astype(np.uint8)

    # 2. Smooth Radial Vignette Mask
    Y, X = np.ogrid[:H, :W]
    cx_v, cy_v = W / 2.0, H / 2.0
    dist_from_center = np.sqrt((X - cx_v) ** 2 + (Y - cy_v) ** 2)
    max_dist = np.sqrt(cx_v ** 2 + cy_v ** 2)
    vignette = 1.0 - vignette_intensity * (dist_from_center / max_dist) ** 1.5
    vignette = np.clip(vignette, 0.4, 1.0)

    darkened = (darkened.astype(np.float32) * vignette[:, :, np.newaxis]).astype(np.uint8)
    return darkened


def overlay_nbf_branding(cv2_img, logo_path=None, target_logo_width=480, **kwargs):
    """
    Overlays the official NBF (NEON BEATS FACTORY) branding on the left side
    centered vertically, matching the brand guidelines.
    """
    H, W = cv2_img.shape[:2]

    if logo_path is None:
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "nbf_logo.png"),
            os.path.join("assets", "nbf_logo.png"),
            os.path.join("..", "assets", "nbf_logo.png"),
        ]
        logo_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not logo_path or not os.path.exists(logo_path):
        print(f"[NBF Branding] Warning: Logo not found at {logo_path}, skipping logo overlay.", flush=True)
        return cv2_img

    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return cv2_img

    # Proportional logo scale (target width ~480px on 1080p canvas)
    scale = (target_logo_width * (H / 1080.0)) / logo.shape[1]
    scaled_w = int(logo.shape[1] * scale)
    scaled_h = int(logo.shape[0] * scale)
    logo_resized = cv2.resize(logo, (scaled_w, scaled_h), interpolation=cv2.INTER_LANCZOS4)

    # Position on left side (centered vertically at cy = 0.50 * H)
    lx = int(W * 0.22 - scaled_w / 2)
    ly = int(H * 0.485 - scaled_h / 2)

    lx = max(0, min(W - scaled_w, lx))
    ly = max(0, min(H - scaled_h, ly))

    # Convert to PIL for smooth text + shadow rendering
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    pil_canvas = Image.fromarray(rgb)
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    # Convert logo to PIL Image
    logo_rgba = cv2.cvtColor(logo_resized, cv2.COLOR_BGRA2RGBA)
    pil_logo = Image.fromarray(logo_rgba)

    # Add soft drop shadow behind logo
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.paste(pil_logo, (lx, ly + 4), pil_logo)
    # Tint shadow black with alpha
    s_arr = np.array(shadow)
    s_arr[:, :, :3] = 0
    s_arr[:, :, 3] = (s_arr[:, :, 3].astype(np.float32) * 0.70).astype(np.uint8)
    shadow = Image.fromarray(s_arr).filter(ImageFilter.GaussianBlur(8))

    overlay = Image.alpha_composite(overlay, shadow)
    overlay.paste(pil_logo, (lx, ly), pil_logo)

    pil_canvas = Image.alpha_composite(pil_canvas.convert('RGBA'), overlay)
    return cv2.cvtColor(np.array(pil_canvas), cv2.COLOR_RGBA2BGR)


def compute_audio_rhythm(mono_audio, sr, fps=60):
    """
    Analyzes kick transients (sub-bass 25-130 Hz) for authentic Avee BeatPulse,
    along with overall spectral energy for smooth visualizer dynamics.
    """
    total_frames = int(len(mono_audio) / sr * fps)
    hop_length = int(sr / fps)
    n_fft = 2048

    frequencies, times, Zxx = scipy.signal.stft(
        mono_audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length
    )
    magnitude = np.abs(Zxx)

    # Sub-bass for drum kicks (25 Hz to 130 Hz)
    bass_idx = np.where((frequencies >= 25) & (frequencies <= 130))[0]
    bass_energy = np.mean(magnitude[bass_idx, :], axis=0) if len(bass_idx) > 0 else np.zeros(magnitude.shape[1])

    # Overall spectral energy (energy envelope)
    total_energy = np.mean(magnitude, axis=0)

    # Truncate / pad
    if len(bass_energy) < total_frames:
        bass_energy = np.pad(bass_energy, (0, total_frames - len(bass_energy)))
        total_energy = np.pad(total_energy, (0, total_frames - len(total_energy)))
    else:
        bass_energy = bass_energy[:total_frames]
        total_energy = total_energy[:total_frames]

    # Beat smoothing with fast attack & natural exponential decay (~120ms kick feel)
    smoothed_bass = np.zeros(total_frames, dtype=np.float32)
    smoothed_energy = np.zeros(total_frames, dtype=np.float32)

    attack_rate = 0.82
    decay_rate = 0.085

    for i in range(total_frames):
        b_curr = bass_energy[i]
        e_curr = total_energy[i]
        if i == 0:
            smoothed_bass[i] = b_curr
            smoothed_energy[i] = e_curr
        else:
            if b_curr > smoothed_bass[i - 1]:
                smoothed_bass[i] = smoothed_bass[i - 1] + (b_curr - smoothed_bass[i - 1]) * attack_rate
            else:
                smoothed_bass[i] = smoothed_bass[i - 1] - (smoothed_bass[i - 1] - b_curr) * decay_rate

            if e_curr > smoothed_energy[i - 1]:
                smoothed_energy[i] = smoothed_energy[i - 1] + (e_curr - smoothed_energy[i - 1]) * attack_rate
            else:
                smoothed_energy[i] = smoothed_energy[i - 1] - (smoothed_energy[i - 1] - e_curr) * 0.05

    # Normalize to [0.0, 1.0] with soft sigmoid curve
    b_max = np.percentile(smoothed_bass, 97) if len(smoothed_bass) > 0 else 1.0
    if b_max > 0:
        norm_bass = np.clip(smoothed_bass / b_max, 0.0, 1.5)
    else:
        norm_bass = np.zeros_like(smoothed_bass)

    e_max = np.percentile(smoothed_energy, 95) if len(smoothed_energy) > 0 else 1.0
    if e_max > 0:
        norm_energy = np.clip(smoothed_energy / e_max, 0.0, 1.5)
    else:
        norm_energy = np.zeros_like(smoothed_energy)

    return norm_bass, norm_energy


def extract_artwork_color(img_bgr, mode="auto"):
    """
    Intelligently extracts visualizer neon glow color from the background artwork:
    - 'auto': Identifies the dominant vibrant hue, weighted by saturation, and boosts
              it into an intense EDM neon glow matching the artwork's atmosphere.
    - 'complementary': Rotates the dominant hue by 180 degrees on the color wheel
              to guarantee maximum contrast and pop against any background.
    - If the artwork has low saturation / no dominant hue, falls back to a cool neon
      palette color so the visualizer always looks vibrant and striking.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Filter for vibrant, non-muddy pixels (sufficient saturation and brightness)
    mask = (s > 60) & (v > 50)
    if not np.any(mask):
        mask = (s > 35) & (v > 40)
    if not np.any(mask):
        mask = v > 40

    valid_h = h[mask]
    valid_s = s[mask]

    # If the image is largely monochromatic / grayscale (very low saturation throughout)
    # pick a cool vibrant signature neon color so the visualizer always looks awesome!
    if len(valid_s) == 0 or np.mean(valid_s) < 30:
        cool_neon_fallbacks = [
            (250, 240, 60),   # Electric Cyan
            (70, 215, 255),   # Radiant Gold
            (210, 140, 255),  # Cyber Rose Pink
            (255, 60, 220),   # Neon Magenta
            (80, 255, 120),   # Toxic Lime
            (255, 130, 180),  # Electric Violet
            (255, 225, 140),  # Frosted Sky
        ]
        idx = int(np.sum(img_bgr[:10, :10])) % len(cool_neon_fallbacks)
        return cool_neon_fallbacks[idx]

    # Compute histogram weighted by pixel saturation so vivid elements take priority
    weights = valid_s.astype(np.float32) / 255.0
    hist, bin_edges = np.histogram(valid_h, bins=18, range=(0, 180), weights=weights)
    dom_bin = np.argmax(hist)
    dom_hue = int((bin_edges[dom_bin] + bin_edges[dom_bin + 1]) / 2)

    if mode == "complementary":
        dom_hue = (dom_hue + 90) % 180

    # Luminous neon: high saturation (245/255), maximum value (255/255)
    neon_hsv = np.uint8([[[dom_hue, 245, 255]]])
    neon_bgr = cv2.cvtColor(neon_hsv, cv2.COLOR_HSV2BGR)[0][0]
    return tuple(int(c) for c in neon_bgr)


def generate_nbf_video(
    viz_path,
    bg_path,
    audio_path,
    output_path,
    fps=60,
    base_diameter=688,
    color="cyan",
    darken_factor=0.50,
    song_title=None,
    target_width=1920,
    target_height=1080,
    crf=19,
    start_sec=0.0,
    duration=None,
):
    """
    Renders the complete 60 FPS NBF music video with:
    1. Background darkening mask & vignette
    2. NBF branding logo on left
    3. Beat-responsive cyan core visualizer on right
    4. Fast raw FFmpeg pipe encoding
    """
    W, H = target_width, target_height

    # 1. Load background image first so dynamic color extraction can analyze it
    raw_bg = cv2.imread(bg_path)
    if raw_bg is None:
        raise ValueError(f"Could not load image: {bg_path}")

    # 2. Resolve visualizer color
    if isinstance(color, str):
        c_low = color.lower().strip()
        if c_low in ("auto", "harmonized"):
            color_bgr = extract_artwork_color(raw_bg, mode="auto")
        elif c_low in ("complementary", "contrast"):
            color_bgr = extract_artwork_color(raw_bg, mode="complementary")
        elif c_low == "random":
            import random
            color_bgr = random.choice(list(NEON_PALETTE.values()))
        elif c_low.startswith("#") or (len(c_low) == 6 and all(c in "0123456789abcdef" for c in c_low)):
            hex_str = c_low.lstrip("#")
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            color_bgr = (b, g, r)
        else:
            color_bgr = NEON_PALETTE.get(c_low, NEON_PALETTE["cyan"])
    else:
        color_bgr = color

    print(f"\n[NBF Visualizer] Starting video render ({W}x{H} @ {fps}fps)...")
    print(f"  - Background: {bg_path}")
    print(f"  - Audio: {audio_path}")
    print(f"  - Darkening factor: {darken_factor} (Mask applied)")
    print(f"  - Neon color BGR: {color_bgr} (Mode: {color})")
    print(f"  - Core diameter: {base_diameter}px")

    bh, bw = raw_bg.shape[:2]
    target_ratio = W / float(H)
    orig_ratio = bw / float(bh)
    if orig_ratio > target_ratio:
        crop_w = int(bh * target_ratio)
        left = (bw - crop_w) // 2
        bg = raw_bg[:, left:left + crop_w]
    else:
        crop_h = int(bw / target_ratio)
        top = (bh - crop_h) // 2
        bg = raw_bg[top:top + crop_h, :]

    bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_LANCZOS4)

    # 3. Apply Darkening Mask
    bg = apply_darkening_mask(bg, darken_factor=darken_factor, vignette_intensity=0.25)

    # 4. Overlay NBF Branding on the left side
    bg = overlay_nbf_branding(bg)

    # 5. Load Visualizer Core Frames from .viz file
    template_frames = load_viz_core(viz_path, color_bgr=color_bgr)
    num_template_frames = len(template_frames)

    # 6. Audio rhythm analysis
    print(f"[NBF Visualizer] Loading audio: {audio_path}", flush=True)
    audio_full, sr = sf.read(audio_path)
    if audio_full.ndim > 1:
        mono_full = np.mean(audio_full, axis=1)
    else:
        mono_full = audio_full

    total_duration = len(mono_full) / sr
    start_sample = int(start_sec * sr)
    if duration is not None and duration > 0:
        actual_duration = min(duration, total_duration - start_sec)
        num_samples = int(actual_duration * sr)
        audio_slice = audio_full[start_sample:start_sample + num_samples]
        mono_slice = mono_full[start_sample:start_sample + num_samples]
    else:
        actual_duration = total_duration - start_sec
        audio_slice = audio_full[start_sample:]
        mono_slice = mono_full[start_sample:]

    actual_frames = int(actual_duration * fps)
    print(f"[NBF Visualizer] Audio duration: {actual_duration:.2f}s ({actual_frames} frames @ {fps}fps)", flush=True)

    # Save temporary sync WAV
    temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix="_nbf_sync.wav")
    os.close(temp_wav_fd)
    sf.write(temp_wav_path, audio_slice, sr)

    # Analyze BeatPulse
    bass_env, energy_env = compute_audio_rhythm(mono_slice, sr, fps=fps)

    # 7. Setup Visualizer Coordinates (Right-side placement matching screenshot)
    cx = int(W * 0.741)
    cy = int(H * 0.485)

    max_reach = int(base_diameter * 1.65)
    x1 = max(0, cx - max_reach // 2)
    x2 = min(W, cx + max_reach // 2)
    y1 = max(0, cy - max_reach // 2)
    y2 = min(H, cy + max_reach // 2)
    rcx = cx - x1
    rcy = cy - y1

    bg_roi_static = bg[y1:y2, x1:x2].copy()

    # 8. Launch FFmpeg encoder
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-i", temp_wav_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        output_path
    ]

    print("[NBF Visualizer] Launching FFmpeg raw encoder...", flush=True)
    proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    t0 = time.time()
    last_print = t0
    phase_accum = 0.0

    # Thumbnail snapshot frame
    thumb_frame_idx = min(actual_frames - 1, int(max(2.0, min(actual_duration * 0.35, 8.0)) * fps))
    saved_thumb = None

    try:
        for i in range(actual_frames):
            bass_val = float(bass_env[i])
            energy_val = float(energy_env[i])

            # Continuous rotation phase
            phase_accum += 0.85
            tpl_idx = int(phase_accum) % num_template_frames
            core_src = template_frames[tpl_idx]

            # Dynamic BeatPulse diameter expansion
            # Bass kick expands the core up to 18% dynamically
            scale = 1.0 + (bass_val * 0.18) + (energy_val * 0.05)
            curr_dia = int(round(base_diameter * scale))

            # Resize animated core
            core_scaled = cv2.resize(core_src, (curr_dia, curr_dia), interpolation=cv2.INTER_LINEAR)

            # Flash bloom intensity on drum hits
            if bass_val > 0.45:
                flash_mult = 1.0 + (bass_val - 0.45) * 0.65
                core_scaled = np.clip(core_scaled.astype(np.float32) * flash_mult, 0, 255).astype(np.uint8)

            # Composite onto background ROI
            frame_roi = bg_roi_static.copy()

            # Coordinates within ROI
            px1 = rcx - curr_dia // 2
            px2 = px1 + curr_dia
            py1 = rcy - curr_dia // 2
            py2 = py1 + curr_dia

            # Clip bounds
            spx1 = max(0, px1)
            spx2 = min(frame_roi.shape[1], px2)
            spy1 = max(0, py1)
            spy2 = min(frame_roi.shape[0], py2)

            c_crop_x1 = max(0, -px1)
            c_crop_x2 = c_crop_x1 + (spx2 - spx1)
            c_crop_y1 = max(0, -py1)
            c_crop_y2 = c_crop_y1 + (spy2 - spy1)

            if spx2 > spx1 and spy2 > spy1:
                roi_slice = frame_roi[spy1:spy2, spx1:spx2]
                core_slice = core_scaled[c_crop_y1:c_crop_y2, c_crop_x1:c_crop_x2]
                # Screen blend mode: 255 - ((255 - A) * (255 - B) / 255)
                blended = 255 - (((255 - roi_slice.astype(np.uint16)) * (255 - core_slice.astype(np.uint16))) // 255)
                frame_roi[spy1:spy2, spx1:spx2] = blended.astype(np.uint8)

            # Paste ROI back into full frame
            full_frame = bg.copy()
            full_frame[y1:y2, x1:x2] = frame_roi

            # Save snapshot for thumbnail
            if i == thumb_frame_idx or (saved_thumb is None and i > fps):
                saved_thumb = full_frame.copy()

            # Pipe to FFmpeg
            proc.stdin.write(full_frame.tobytes())

            # Progress log every 3 seconds
            now = time.time()
            if now - last_print >= 3.0 or i == actual_frames - 1:
                pct = ((i + 1) / actual_frames) * 100
                speed = (i + 1) / (now - t0 + 0.001)
                print(f"[NBF Visualizer] Render progress: {pct:.1f}% ({i + 1}/{actual_frames} frames) @ {speed:.1f} fps", flush=True)
                last_print = now

    finally:
        if proc.stdin:
            try:
                proc.stdin.close()
            except Exception:
                pass
        proc.wait()

        # Clean up temporary WAV
        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception:
                pass

    total_time = time.time() - t0
    print(f"\n[NBF Visualizer] Video render finished in {total_time:.1f}s.")

    # 9. Save Matching High-Impact Thumbnail
    thumb_path = output_path.replace(".mp4", "_thumb.jpg")
    if saved_thumb is not None:
        cv2.imwrite(thumb_path, saved_thumb, [cv2.IMWRITE_JPEG_QUALITY, 96])
        print(f"[NBF Visualizer] Matching thumbnail saved: {thumb_path}")

    return output_path, thumb_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NBF Music Video & Thumbnail Generator")
    parser.add_argument("--image", required=True, help="Background image path")
    parser.add_argument("--audio", required=True, help="Audio track path (MP3/WAV)")
    parser.add_argument("--output", default="output_nbf.mp4", help="Output MP4 video path")
    parser.add_argument("--title", default=None, help="Song title")
    parser.add_argument("--duration", type=float, default=None, help="Max duration in seconds (for preview/testing)")
    parser.add_argument("--darken", type=float, default=0.50, help="Darkening mask factor (0.1 to 1.0)")
    parser.add_argument("--color", default="cyan", help="Neon glow color (cyan, gold, pink, etc.)")

    args = parser.parse_args()

    viz_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Visualizer_Core_Only.viz")
    if not os.path.exists(viz_file):
        viz_file = "Visualizer_Core_Only.viz"

    generate_nbf_video(
        viz_path=viz_file,
        bg_path=args.image,
        audio_path=args.audio,
        output_path=args.output,
        duration=args.duration,
        darken_factor=args.darken,
        color=args.color,
        song_title=args.title
    )
