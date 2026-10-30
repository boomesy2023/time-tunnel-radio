# -*- coding: utf-8 -*-
"""把 stations.js 内嵌进 app_template.html，生成单文件 index.html"""
import os, json, re

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "stations.js"), encoding="utf-8") as f:
    raw = f.read()
m = re.search(r"=\s*(\[.*\]);?\s*$", raw, re.S)
data = json.loads(m.group(1))

js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
js = js.replace("</", "<\\/")           # 防止意外闭合 script 标签
payload = "window.EMBEDDED_STATIONS = " + js + ";"

with open(os.path.join(BASE, "app_template.html"), encoding="utf-8") as f:
    tpl = f.read()

with open(os.path.join(BASE, "icons.html"), encoding="utf-8") as f:
    icons = f.read().strip()

with open(os.path.join(BASE, "globe_map.svg"), encoding="utf-8") as f:
    globe_svg = f.read().strip()

assert "/*__EMBEDDED_STATIONS__*/" in tpl, "模板占位符丢失"
assert "<!--__ICONS__-->" in tpl, "图标占位符丢失"
assert tpl.count("<!--__GLOBE_MAP__-->") == 2, "地球占位符需要恰好两份"
out = (tpl.replace("/*__EMBEDDED_STATIONS__*/", payload)
          .replace("<!--__ICONS__-->", icons)
          .replace("<!--__GLOBE_MAP__-->", globe_svg))

dst = os.path.join(BASE, "index.html")
with open(dst, "w", encoding="utf-8") as f:
    f.write(out)
print("生成", dst, os.path.getsize(dst), "bytes，电台数:", len(data))
