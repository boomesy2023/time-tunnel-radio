# -*- coding: utf-8 -*-
"""抓取 Radio Browser 电台数据，生成内嵌电台库 stations.js"""
import json, urllib.request, urllib.parse, ssl, sys, os
from concurrent.futures import ThreadPoolExecutor

BASE = "https://de1.api.radio-browser.info"
UA = {"User-Agent": "TimeTunnelRadio/1.0"}

def get(path, timeout=30):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

jobs = []
# 1) 按热度分页取 6 页 x 150
for off in range(0, 900, 150):
    jobs.append("/json/stations/search?limit=150&offset=%d&hidebroken=true&order=clickcount&reverse=true" % off)
# 2) 随机 3 批，增加多样性
for i in range(3):
    jobs.append("/json/stations/search?limit=150&offset=0&hidebroken=true&order=random")
# 3) 每个主要国家取一批
COUNTRIES = ["US","GB","JP","KR","FR","DE","IT","ES","BR","CN","CA","AU","NL","RU","IN","TR","MX","PL","SE","TH","GR","PT","AR","ID","PH","VN","MY","SG","NO","FI","DK","CH","AT","BE","IE","NZ","ZA","EG","SA","IL","UA","CZ","HU","RO","CL","CO","PE","HK","TW"]
for c in COUNTRIES:
    jobs.append("/json/stations/search?limit=120&hidebroken=true&countrycode=%s&order=clickcount&reverse=true" % c)

def fetch(p):
    try:
        return get(p, timeout=40)
    except Exception as e:
        print("FAIL", p, e, file=sys.stderr)
        return []

print("总请求数:", len(jobs))
raw = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for res in ex.map(fetch, jobs):
        raw.extend(res or [])
print("原始条目:", len(raw))

seen, out = set(), []
GOOD_CODEC = {"MP3","AAC","AAC+","OGG","OPUS","FLAC","HLS","MP4"}
for s in raw:
    u = s.get("url_resolved") or s.get("url") or ""
    if not u:
        continue
    if s.get("lastcheckok") != 1:
        continue
    # 优先 https，避免浏览器混合内容拦截
    if not u.startswith("https://"):
        continue
    uuid = s.get("stationuuid")
    if not uuid or uuid in seen:
        continue
    name = (s.get("name") or "").strip()
    if not name or len(name) > 60:
        continue
    if (s.get("bitrate") or 0) < 32:
        continue
    codec = (s.get("codec") or "").upper()
    if codec and codec not in GOOD_CODEC:
        continue
    fav = s.get("favicon") or ""
    if fav and not fav.startswith("https://"):
        fav = ""
    seen.add(uuid)
    out.append({
        "u": uuid,
        "n": name,
        "s": u,
        "c": s.get("country") or "",
        "cc": s.get("countrycode") or "",
        "t": (s.get("tags") or "").split(",")[:3],
        "b": s.get("bitrate") or 0,
        "k": codec,
        "p": int(s.get("clickcount") or 0),
        "f": fav,
    })

out.sort(key=lambda x: -x["p"])
# 每个国家最多保留 14 个，保证全球分布
per_country, final = {}, []
for st in out:
    cc = st["cc"] or "ZZ"
    if per_country.get(cc, 0) >= 14:
        continue
    per_country[cc] = per_country.get(cc, 0) + 1
    final.append(st)

print("入选电台:", len(final), "国家/地区数:", len(per_country))
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stations.js")
with open(dst, "w", encoding="utf-8") as f:
    f.write("window.EMBEDDED_STATIONS = " + json.dumps(final, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("已写入:", dst, os.path.getsize(dst), "bytes")
from collections import Counter
print("分布 TOP15:", Counter([s["cc"] for s in final]).most_common(15))
