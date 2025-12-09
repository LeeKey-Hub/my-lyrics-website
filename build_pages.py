import os
try:
    from pypinyin import pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False
    print("⚠️ 'pypinyin' not found. Pinyin will be missing unless manually added.")

# ==========================================
# 1. THE DESIGN (HTML TEMPLATE)
# ==========================================
# This applies the Dark Mode / Spotify style to ALL songs automatically.
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title_en} - Learning Mode</title>
    <style>
      :root {{
        --bg-color: #121212;
        --card-bg: #181818;
        --text-main: #ffffff;
        --text-sub: #b3b3b3;
        --accent: #1db954;
        --border-color: #282828;
      }}
      body {{ font-family: "Circular", "Segoe UI", sans-serif; background-color: var(--bg-color); color: var(--text-main); line-height: 1.6; margin: 0; padding-bottom: 80px; }}
      
      .nav-bar {{ background-color: rgba(18, 18, 18, 0.95); padding: 15px 20px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; backdrop-filter: blur(10px); }}
      .back-btn {{ color: var(--text-sub); text-decoration: none; font-size: 0.9em; font-weight: bold; display: flex; align-items: center; }}
      .back-btn:hover {{ color: var(--text-main); }}
      .back-btn::before {{ content: "←"; margin-right: 8px; font-size: 1.2em; }}
      
      .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
      .song-header {{ text-align: center; margin: 30px 0 40px 0; }}
      h1 {{ font-size: 2.5em; margin-bottom: 5px; }}
      .sub-header {{ color: var(--accent); font-size: 1.1em; font-weight: 500; }}
      
      /* Tools */
      .tools-bar {{ display: flex; justify-content: center; gap: 15px; margin-top: 15px; }}
      .tool-btn {{ background-color: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-sub); padding: 8px 15px; border-radius: 20px; font-size: 0.85em; text-decoration: none; transition: 0.2s; }}
      .tool-btn:hover {{ border-color: var(--accent); color: var(--accent); }}

      h2.section-title {{ color: var(--text-main); font-size: 1.5em; margin-top: 50px; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }}
      
      /* Vocab Cards */
      .vocab-card {{ background: var(--card-bg); border-radius: 12px; margin-bottom: 25px; border: 1px solid var(--border-color); overflow: hidden; }}
      .card-header {{ background: linear-gradient(90deg, rgba(29,185,84,0.1) 0%, rgba(24,24,24,0) 100%); padding: 15px 25px; border-left: 5px solid var(--accent); display: flex; justify-content: space-between; align-items: center; }}
      .header-word {{ font-size: 1.5em; font-weight: 700; }}
      .header-pinyin {{ color: var(--accent); margin-left: 10px; }}
      .card-body {{ padding: 20px 25px; }}
      .concept-row {{ display: flex; margin-bottom: 15px; border-bottom: 1px dashed #333; padding-bottom: 15px; }}
      .concept-row:last-child {{ border-bottom: none; }}
      .concept-label {{ width: 80px; color: var(--text-sub); font-size: 0.75em; text-transform: uppercase; }}
      
      /* Lyrics Table */
      .lyrics-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
      .lyrics-table th {{ text-align: left; color: var(--text-sub); font-size: 0.85em; padding: 10px 15px; border-bottom: 1px solid var(--border-color); }}
      .lyrics-table tr:hover {{ background-color: #222; }}
      .lyrics-table td {{ padding: 18px 15px; vertical-align: top; }}
      .hanzi-lyric {{ font-size: 1.2em; font-weight: 500; width: 35%; }}
      .pinyin-lyric {{ color: var(--accent); width: 30%; }}
      .eng-lyric {{ color: var(--text-sub); font-size: 0.95em; width: 35%; }}
      
      @media (max-width: 600px) {{
        .lyrics-table th {{ display: none; }}
        .lyrics-table td {{ display: block; width: 100%; padding: 4px 15px; }}
        .hanzi-lyric {{ padding-top: 15px; }}
        .eng-lyric {{ padding-bottom: 15px; }}
      }}
    </style>
</head>
<body>
    <nav class="nav-bar"><a href="index.html" class="back-btn">Back to Library</a></nav>
    <div class="container">
        <div class="song-header">
            <h1>{title_cn}</h1>
            <div class="sub-header">{title_en}</div>
            <div class="tools-bar">
                <a href="https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdq={title_cn}" target="_blank" class="tool-btn">📖 Dictionary</a>
                <a href="https://translate.google.com/?sl=zh-CN&tl=en&text={title_cn}&op=translate" target="_blank" class="tool-btn">🌏 Translate</a>
            </div>
        </div>

        <h2 class="section-title">Deep Dive Vocabulary</h2>
        {vocab_html}

        <h2 class="section-title">Lyrics Breakdown</h2>
        <table class="lyrics-table">
            <thead><tr><th>Hanzi</th><th>Pinyin</th><th>Meaning</th></tr></thead>
            <tbody>
                {lyrics_html}
            </tbody>
        </table>
        <div style="text-align:center; margin-top:50px; color:#555;">Generated by build_pages.py</div>
    </div>
</body>
</html>
"""

# ==========================================
# 2. THE CONTENT (DATA)
# ==========================================
# Add your 6 songs here. I did the first one completely for you.
songs_data = [
    {
        "filename": "1.挪威的森林 (Norwegian Wood).html",
        "title_cn": "挪威的森林",
        "title_en": "Norwegian Wood",
        
        # VOCAB SECTION (Optional - leave empty [] if none)
        "vocab": [
            {
                "word": "融化", "pinyin": "róng huà", "meaning": "To Melt",
                "sent_cn": "她的微笑让我的心融化了。", "sent_en": "Her smile melted my heart."
            },
            {
                "word": "宁静", "pinyin": "níng jìng", "meaning": "Tranquil",
                "sent_cn": "夜晚的森林非常宁静。", "sent_en": "The forest at night is very tranquil."
            },
             {
                "word": "澄清", "pinyin": "chéng qīng", "meaning": "Clear / Clarify",
                "sent_cn": "湖水很澄清。", "sent_en": "The lake water is very clear."
            }
        ],

        # LYRICS SECTION - Just pasted the Chinese lines. 
        # Python will handle the HTML table structure.
        # Format: (Chinese, English Translation)
        "lyrics_raw": [
            ("让我将你心儿摘下", "Let me take off your heart"),
            ("试着将它慢慢溶化", "Try to melt it slowly"),
            ("看我在你心中是否仍完美无瑕", "See if I am still perfect in your heart"),
            ("是否依然爲我丝丝牵挂", "Do you still worry about me a little?"),
            ("依然爱我无法自拔", "Still love me uncontrollably"),
            ("心中是否有我未曾到过的地方啊", "Is there a place in your heart I haven't been?"),
            ("那裏湖面总是澄清", "The lake surface there is always clear"),
            ("那裏空气充满宁静", "The air there is full of tranquility"),
            ("雪白明月照在大地", "Snow-white moon shines on the earth"),
            ("藏著你不愿提起的回忆", "Hiding memories you don't want to mention"),
            ("你要真心总是可以从头", "You say a true heart can always start over"),
            ("真爱总是可以长久", "True love can always last long"),
            ("为何你的眼神还有孤独时的落寞", "Why do your eyes still have that loneliness?"),
            ("是否我只是你一种寄托", "Am I just an emotional support for you?"),
            ("填满你感情的缺口", "Filling the void in your emotions"),
            ("心中那片森林何时能让我停留", "When will that forest in your heart let me stay?"),
            ("那裏湖面总是澄清", "The lake surface there is always clear"),
            ("那裏空气充满宁静", "The air there is full of tranquility"),
            ("雪白明月照在大地", "Snow-white moon shines on the earth"),
            ("藏著你最深处的祕密", "Hiding your deepest secrets"),
            ("或许我 不该问", "Maybe I shouldn't ask"),
            ("让你平静的心再起涟漪", "Causing ripples in your calm heart"),
            ("只是爱你的心超出了界线", "But my love for you crossed the line"),
            ("我想拥有你所有一切", "I want to own everything about you"),
            ("应该是 我不该问", "It must be that I shouldn't ask"),
            ("不该让你再将往事重提", "Shouldn't make you bring up the past again"),
            ("只是心中枷锁", "It's just the shackles in my heart"),
            ("该如何才能解脱", "How can I break free?")
            # Note: I shortened the repetitive parts for the example, 
            # but you can paste the WHOLE list here.
        ]
    }
    # ADD SONG 2 HERE...
    # ADD SONG 3 HERE...
]

# ==========================================
# 3. THE LOGIC (GENERATOR)
# ==========================================
def generate_pinyin(text):
    if HAS_PYPINYIN:
        # Generate pinyin, capitalize first letter
        raw_py = pinyin(text, style=Style.TONE)
        flat_py = " ".join([x[0] for x in raw_py])
        return flat_py
    return "..." # Placeholder if library not installed

def build_files():
    for song in songs_data:
        print(f"🔨 Building: {song['title_en']}...")
        
        # 1. Build Vocab HTML
        vocab_html = ""
        for v in song['vocab']:
            vocab_html += f"""
            <div class="vocab-card">
                <div class="card-header">
                    <div><span class="header-word">{v['word']}</span><span class="header-pinyin">{v['pinyin']}</span></div>
                    <span class="header-meaning">{v['meaning']}</span>
                </div>
                <div class="card-body">
                    <div class="concept-row">
                        <div class="concept-label">Example</div>
                        <div>
                            <div>{v['sent_cn']}</div>
                            <div style="color:var(--accent); font-size:0.9em; font-style:italic;">{generate_pinyin(v['sent_cn'])}</div>
                            <div style="color:var(--text-sub); font-size:0.9em;">{v['sent_en']}</div>
                        </div>
                    </div>
                </div>
            </div>
            """

        # 2. Build Lyrics HTML
        lyrics_html = ""
        for line in song['lyrics_raw']:
            cn_text = line[0]
            en_text = line[1]
            py_text = generate_pinyin(cn_text)
            
            lyrics_html += f"""
            <tr>
                <td class="hanzi-lyric">{cn_text}</td>
                <td class="pinyin-lyric">{py_text}</td>
                <td class="eng-lyric">{en_text}</td>
            </tr>
            """

        # 3. Combine into final HTML
        full_html = HTML_TEMPLATE.format(
            title_cn=song['title_cn'],
            title_en=song['title_en'],
            vocab_html=vocab_html,
            lyrics_html=lyrics_html
        )

        # 4. Save File
        with open(song['filename'], "w", encoding="utf-8") as f:
            f.write(full_html)
            
    print("✅ All song pages updated successfully!")

if __name__ == "__main__":
    build_files()
