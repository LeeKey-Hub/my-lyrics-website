import os
import re
import urllib.parse
from bs4 import BeautifulSoup
from pypinyin import pinyin, Style

# --- CONFIGURATION ---
ROOT_DIR = os.getcwd()
SONGS_DIR = os.path.join(ROOT_DIR, "songs")
IMAGES_DIR = os.path.join(ROOT_DIR, "assets", "images")

# Links in the HTML need to point to these folders
WEB_SONG_PREFIX = "songs/"
WEB_IMG_PREFIX = "assets/images/"

html_head = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chinese Song Library</title>
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #181818;
            --card-hover: #282828;
            --text-main: #ffffff;
            --text-sub: #b3b3b3;
            --accent: #1db954;
        }
        body {
            font-family: "Circular", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }
        .container { max-width: 1200px; margin: 0 auto; padding-bottom: 50px; }
        
        header { display: flex; flex-direction: column; align-items: center; margin-bottom: 40px; padding-top: 20px; }
        h1 { font-size: 3em; margin-bottom: 10px; letter-spacing: -1px; text-align: center; }
        p.subtitle { color: var(--text-sub); font-size: 1.1em; margin-bottom: 30px; }

        /* Search */
        .search-container { position: relative; width: 100%; max-width: 500px; }
        #searchInput {
            width: 100%; padding: 15px 25px; border-radius: 50px;
            border: 1px solid #333; background-color: #2a2a2a; color: white;
            font-size: 1.1em; outline: none; transition: 0.3s; box-sizing: border-box;
        }
        #searchInput:focus { border-color: var(--accent); background-color: #333; }

        /* Grid */
        .song-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 24px;
            margin-top: 20px;
        }

        /* Cards */
        .song-card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 16px;
            text-decoration: none;
            color: inherit;
            transition: background-color 0.3s ease;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .song-card:hover { background-color: var(--card-hover); }

        .card-img-box {
            width: 100%; aspect-ratio: 1 / 1;
            border-radius: 6px; overflow: hidden; margin-bottom: 12px;
            position: relative; box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            background: #333;
        }
        .card-img-box img {
            width: 100%; height: 100%; object-fit: cover;
            transition: transform 0.3s ease;
        }
        .song-card:hover .card-img-box img { transform: scale(1.05); }

        /* Genre Pill - UPDATED LAYOUT */
        .genre-pill {
            /* Positioned relative to flow, not absolute over image */
            display: inline-block;
            font-size: 0.65em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px; /* Space between pill and title */
            
            /* Visual Style: Outlined Accent */
            color: #ffb74d;
            border: 1px solid rgba(255, 183, 77, 0.3);
            background: rgba(255, 183, 77, 0.1); 
            padding: 2px 8px;
            border-radius: 4px;
            align-self: flex-start;
            width: fit-content;
        }

        /* Play Button Overlay */
        .play-overlay {
            position: absolute; bottom: 8px; right: 8px;
            width: 48px; height: 48px; border-radius: 50%;
            background-color: var(--accent);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; transform: translateY(8px); transition: all 0.3s ease;
            z-index: 2;
        }
        .play-overlay::after { content: "▶"; font-size: 1.2em; color: black; margin-left: 2px; }
        .song-card:hover .play-overlay { opacity: 1; transform: translateY(0); }

        /* Text Info */
        .song-title {
            font-size: 1.1em; font-weight: 700; color: var(--text-main);
            margin: 0 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .song-pinyin {
            font-size: 0.85em; color: #ffd54f; font-weight: 500; margin-bottom: 4px;
        }
        .song-artist {
            font-size: 0.9em; color: var(--text-sub); margin: 0;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .footer { text-align: center; margin-top: 60px; color: #555; font-size: 0.8em; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>🎵 Chinese Song Hub</h1>
        <p class="subtitle">Learn Chinese through Lyrics</p>
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Search title, artist or pinyin...">
        </div>
        <div class="tools" style="margin-top: 15px; font-size: 0.9em;">
             <a href="https://www.mdbg.net/chinese/dictionary" target="_blank" style="color:#b3b3b3; text-decoration:none; margin: 0 10px;">📖 Dictionary</a>
             <a href="https://translate.google.com/" target="_blank" style="color:#b3b3b3; text-decoration:none; margin: 0 10px;">G-Translate</a>
        </div>
    </header>
    <div class="song-grid" id="songGrid">
"""

html_footer = """
    </div>
    <div class="footer"><p>Auto-generated by build_index.py</p></div>
</div>

<script>
    const searchInput = document.getElementById('searchInput');
    const songGrid = document.getElementById('songGrid');
    const cards = songGrid.getElementsByClassName('song-card');

    searchInput.addEventListener('keyup', function() {
        const filter = searchInput.value.toLowerCase();
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            const text = card.innerText.toLowerCase();
            if (text.indexOf(filter) > -1) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }
        }
    });
</script>
</body>
</html>
"""

def extract_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        title_tag = soup.select_one('.hero-text h1')
        title = title_tag.text.strip() if title_tag else "Unknown Title"

        subtitle_tag = soup.select_one('.hero-text p')
        full_subtitle = subtitle_tag.text.strip() if subtitle_tag else ""
        
        if "—" in full_subtitle:
            parts = full_subtitle.split("—")
            artist = parts[-1].strip()
        elif "-" in full_subtitle:
            parts = full_subtitle.split("-")
            artist = parts[-1].strip()
        else:
            artist = full_subtitle 

        genre_tag = soup.select_one('.tag-pill')
        genre = genre_tag.text.strip() if genre_tag else "Song"

        # Generate Pinyin
        raw_pinyin = pinyin(title, style=Style.TONE)
        pinyin_str = ' '.join([x[0].capitalize() for x in raw_pinyin])

        return {
            "title": title,
            "artist": artist,
            "genre": genre,
            "pinyin": pinyin_str
        }

    except Exception as e:
        print(f"⚠️ Error parsing {filepath}: {e}")
        return None

def find_matching_image(song_number):
    try:
        if not os.path.exists(IMAGES_DIR):
             return None
             
        available_images = os.listdir(IMAGES_DIR)
        for img in available_images:
            if img.startswith(f"{song_number}."):
                return img
    except FileNotFoundError:
        print("❌ Error: Could not find assets/images folder.")
    return None

# --- MAIN LOGIC ---

if not os.path.exists(SONGS_DIR):
    print(f"❌ Error: The folder '{SONGS_DIR}' does not exist.")
    exit()

files = os.listdir(SONGS_DIR)
songs = []
pattern = re.compile(r'^(\d+)\.')

print(f"📂 Scanning '{SONGS_DIR}' for songs...")

for file in files:
    if file.endswith(".html"):
        full_path = os.path.join(SONGS_DIR, file)
        
        # Extract metadata
        meta = extract_metadata(full_path)
        
        # Get Sorting Number
        match = pattern.match(file)
        sort_num = int(match.group(1)) if match else 999

        # Find Image
        found_image_filename = find_matching_image(sort_num)
        
        if found_image_filename:
            encoded_img_name = urllib.parse.quote(found_image_filename)
            full_img_path = WEB_IMG_PREFIX + encoded_img_name
        else:
            full_img_path = "assets/images/default.png" 

        # Create web-safe path for the song link
        encoded_song_name = urllib.parse.quote(file)
        song_web_link = WEB_SONG_PREFIX + encoded_song_name

        if meta:
            songs.append({
                "num": sort_num,
                "filename": song_web_link, 
                "img": full_img_path,
                **meta 
            })

# Sort by number
songs.sort(key=lambda x: x["num"])

# Generate HTML Cards
cards_html = ""
for song in songs:
    card = f"""
    <a href="{song['filename']}" class="song-card">
        <!-- 1. Image first -->
        <div class="card-img-box">
            <img src="{song['img']}" alt="{song['title']}" loading="lazy">
            <div class="play-overlay"></div>
        </div>
        
        <!-- 2. Genre second (Moved here so it doesn't cover the art) -->
        <span class="genre-pill">{song['genre']}</span>
        
        <!-- 3. Text Info -->
        <div class="song-title">{song['title']}</div>
        <div class="song-pinyin">{song['pinyin']}</div>
        <p class="song-artist">{song['artist']}</p>
    </a>
    """
    cards_html += card

# Write to index.html in the ROOT folder
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_head + cards_html + html_footer)

print(f"✅ Successfully generated index.html with {len(songs)} songs!")
