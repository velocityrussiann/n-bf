"""
Facebook Page Video Publisher - Neon Beats Factory (NBF)
Publishes 60 FPS EDM videos and thumbnails to the official Facebook Page:
https://www.facebook.com/neonbeatsfactory (ID: 538586562680121)
Using Meta Graph API v21.0.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def get_fb_credentials():
    page_id = (os.getenv("FB_PAGE_ID") or "").strip()
    page_token = (os.getenv("FB_PAGE_ACCESS_TOKEN") or "").strip()

    if not page_id or not page_token:
        # Check if we have META_LONG_LIVED_ACCESS_TOKEN to auto-fetch page token
        meta_token = (os.getenv("META_LONG_LIVED_ACCESS_TOKEN") or "").strip()
        if meta_token and not page_token:
            print("[Facebook Auth] Resolving page token from META_LONG_LIVED_ACCESS_TOKEN...")
            try:
                url = "https://graph.facebook.com/v21.0/me/accounts"
                params = {"access_token": meta_token, "limit": 100}
                while url:
                    r = requests.get(url, params=params, timeout=15)
                    for p in r.json().get("data", []):
                        if p.get("id") == "538586562680121" or "neon" in p.get("name", "").lower():
                            page_id = p.get("id")
                            page_token = p.get("access_token")
                            break
                    if page_token:
                        break
                    url = r.json().get("paging", {}).get("next")
                    params = None
            except Exception as e:
                print(f"[Facebook Auth] Warning: Could not resolve page token: {e}")

    return page_id, page_token


def upload_to_facebook_page(
    video_path,
    title,
    description,
    thumb_path=None,
    page_id=None,
    page_token=None
):
    """
    Uploads a video to the Neon Beats Factory Facebook Page via Graph API.
    Returns dict with 'id' and 'url' of the published video.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    if not page_id or not page_token:
        p_id, p_token = get_fb_credentials()
        page_id = page_id or p_id
        page_token = page_token or p_token

    if not page_id or not page_token:
        raise ValueError(
            "Missing Facebook Page credentials! Ensure FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN "
            "(or META_LONG_LIVED_ACCESS_TOKEN) are set."
        )

    def mask(s):
        return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"

    print(f"\n[Facebook Publisher] Publishing to Page ID: {page_id}")
    print(f"  - Title: {title}")
    print(f"  - Video File: {video_path} ({os.path.getsize(video_path) / (1024*1024):.1f} MB)")
    print(f"  - Access Token: {mask(page_token)}")

    upload_url = f"https://graph.facebook.com/v21.0/{page_id}/videos"

    data = {
        "access_token": page_token,
        "title": title[:255],
        "description": description,
    }

    files = {}
    video_fp = open(video_path, "rb")
    files["source"] = (os.path.basename(video_path), video_fp, "video/mp4")

    thumb_fp = None
    if thumb_path and os.path.exists(thumb_path):
        print(f"  - Attaching Thumbnail: {thumb_path}")
        thumb_fp = open(thumb_path, "rb")
        files["thumb"] = (os.path.basename(thumb_path), thumb_fp, "image/jpeg")

    t0 = time.time()
    try:
        print("[Facebook Publisher] Uploading video to Facebook Graph API...", flush=True)
        response = requests.post(upload_url, data=data, files=files, timeout=300)
        elapsed = time.time() - t0

        if response.status_code != 200:
            err_msg = response.text
            try:
                err_json = response.json().get("error", {})
                err_msg = err_json.get("message", err_msg)
            except Exception:
                pass
            raise RuntimeError(f"Facebook Graph API Error ({response.status_code}): {err_msg}")

        res_data = response.json()
        video_id = res_data.get("id")
        fb_url = f"https://www.facebook.com/{page_id}/videos/{video_id}"

        print(f"[Facebook Publisher] SUCCESS! Video published in {elapsed:.1f}s.")
        print(f"  - Video ID: {video_id}")
        print(f"  - Facebook Video URL: {fb_url}")

        return {
            "id": video_id,
            "url": fb_url,
            "page_id": page_id
        }

    finally:
        video_fp.close()
        if thumb_fp:
            thumb_fp.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish_facebook.py <video_path> <title> [description] [thumb_path]")
        sys.exit(1)

    v_path = sys.argv[1]
    v_title = sys.argv[2]
    v_desc = sys.argv[3] if len(sys.argv) > 3 else "Neon Beats Factory (NBF) - Best Electronic Dance Music & EDM Hits"
    t_path = sys.argv[4] if len(sys.argv) > 4 else None

    result = upload_to_facebook_page(v_path, v_title, v_desc, thumb_path=t_path)
    print(f"\nPublished successfully:\n{result}")
