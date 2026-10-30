# -*- coding: utf-8 -*-
"""
从图标库（Remix Icon，经 Iconify API）抓取所需图标：
1) 生成 icons.html —— 内联 SVG sprite（离线可用，不依赖网络）
2) 生成 icon-192.png / icon-512.png —— PWA 图标（用无头浏览器把 SVG 渲染成 PNG）
"""
import os, re, json, subprocess, urllib.request, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.iconify.design/ri/{}.svg"

# 图标名 -> 用途
NAMES = [
    "shuffle-line", "play-fill", "pause-fill", "skip-back-fill", "skip-forward-fill",
    "heart-3-line", "heart-3-fill", "search-line", "radio-2-line", "radio-2-fill",
    "compass-3-line", "settings-4-line", "volume-up-fill", "volume-mute-fill",
    "volume-down-fill", "timer-2-line", "global-line", "wifi-line", "cloud-off-line",
    "close-line", "delete-bin-line", "arrow-down-s-line", "arrow-up-s-line",
    "download-2-line", "keyboard-line", "information-line", "arrow-left-line",
    "broadcast-line", "headphone-line", "music-2-line", "map-pin-2-line",
    "sparkling-2-line", "smartphone-line", "earth-line", "time-line",
    "history-line", "signal-tower-line", "refresh-line", "play-circle-line",
    "star-smile-line", "mic-line", "play-list-2-line",
]

def fetch(name):
    req = urllib.request.Request(API.format(name), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")

def inner(svg):
    m = re.search(r'viewBox="([^"]+)"', svg)
    vb = m.group(1) if m else "0 0 24 24"
    body = re.sub(r'^<svg[^>]*>', "", svg, flags=re.S)
    body = re.sub(r'</svg>\s*$', "", body, flags=re.S).strip()
    return vb, body

def main():
    symbols = []
    ok = 0
    for n in NAMES:
        try:
            vb, body = inner(fetch(n))
            body = re.sub(r'\s(width|height)="[^"]*"', "", body)
            symbols.append(f'<symbol id="i-{n}" viewBox="{vb}">{body}</symbol>')
            ok += 1
        except Exception as e:
            print("  跳过", n, e)
    sprite = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">'
              + "".join(symbols) + "</svg>")
    with open(os.path.join(BASE, "icons.html"), "w", encoding="utf-8") as f:
        f.write(sprite)
    print(f"图标 sprite 生成完毕：{ok}/{len(NAMES)} 个，{len(sprite)} 字节")

    # ---------- PWA 图标：用图标库里的 radio-2-fill 造型 ----------
    _, glyph = inner(fetch("radio-2-fill"))
    glyph = re.sub(r'fill="currentColor"', 'fill="#ffffff"', glyph)
    def icon_svg(size):
        pad = size * 0.20
        inner_box = size - pad * 2
        scale = inner_box / 24.0
        tx, ty = pad, pad
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#6366f1"/><stop offset="0.55" stop-color="#0ea5e9"/><stop offset="1" stop-color="#22d3ee"/>
</linearGradient></defs>
<rect width="{size}" height="{size}" rx="{size*0.22}" fill="url(#g)"/>
<g transform="translate({tx} {ty}) scale({scale})">{glyph}</g>
<circle cx="{size*0.78}" cy="{size*0.245}" r="{size*0.055}" fill="#ffffff" opacity="0.95"/>
</svg>'''

    chrome = None
    for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
        if os.path.exists(p):
            chrome = p
            break
    for size in (192, 512):
        svg_path = os.path.join(BASE, f"_tmp_icon_{size}.svg")
        png_path = os.path.join(BASE, f"icon-{size}.png")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(icon_svg(size))
        done = False
        if chrome:
            try:
                subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--hide-scrollbars", "--force-device-scale-factor=1",
                                f"--window-size={size},{size}",
                                "--default-background-color=00000000",
                                f"--screenshot={png_path}", "file:///" + svg_path.replace("\\", "/")],
                               timeout=90, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                done = os.path.exists(png_path) and os.path.getsize(png_path) > 500
            except Exception as e:
                print("  渲染失败:", e)
        print(f"icon-{size}.png:", "已生成" if done else "未生成（保留旧图标）",
              os.path.getsize(png_path) if os.path.exists(png_path) else "")
        if not done:
            shutil.copyfile(svg_path.replace(".svg", ".svg"), svg_path)  # 保留 svg 便于手动转换
        os.remove(svg_path)

if __name__ == "__main__":
    main()
