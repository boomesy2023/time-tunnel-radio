# 时空电台 · 全球电台收听系统 📻🌍

一个纯前端的全球电台收听器。首页是一颗**真实大陆轮廓的自转玻璃地球**，点一下就随机接入地球上某个正在播出的电台；也可以按国家、曲风去「发现」页挑台。

**在线体验：** https://boomesy2023.github.io/time-tunnel-radio/

## 功能

- 🌀 **首页 · 随机穿越**：点击「随机接入电台」随机连入全球电台，地球会加速自转做扫描动效，连上后进入播放页
- 🌍 **发现页**：按国家 / 地区（47 个）与曲风（21 类）组合筛选，或关键词搜索；筛选胶囊默认折叠，页面清爽
- 💗 **我的**：收藏 + 收听历史（本地保存，上限 60 条，可清空）
- ⏱ **定时关闭**：15 / 30 / 45 / 60 / 90 分钟，到点自动停播
- ⌨️ **快捷键**：`空格` 播放暂停 · `←`/`P` 上一站 · `→`/`N` 下一站 · `F` 收藏 · `M` 静音 · `↑↓` 音量 · `Enter` 随机穿越
- 📱 **PWA**：可添加到主屏幕，离线打开外壳后仍能用内置电台库收听
- 🛡 **容错**：流地址 9 秒未起播自动换下一站（最多 4 次），不会卡死

## 数据源

[Radio Browser](https://www.radio-browser.info/) 公开电台数据库（全球 5 万+ 电台）。应用内置了 **759 个真实电台、88 个国家 / 地区、全部 HTTPS 流**，断网或在线接口不可用也能正常收听；联网时会自动接入在线库扩展电台池。

## 目录结构

| 文件 | 说明 |
| --- | --- |
| `index.html` | **成品单文件应用**（329KB，含内嵌电台库 / 地球地图 / 图标 sprite），双击即可用 |
| `app_template.html` | 页面模板（源码） |
| `build.py` | 构建脚本：把电台数据、地球地图、图标注入模板 → 生成 `index.html` |
| `stations.js` | 内置电台数据 |
| `fetch_stations.py` | 抓取 Radio Browser 电台数据，生成 `stations.js` |
| `globe_map.svg` / `make_globe.py` | 地球大陆轮廓：Natural Earth 数据 → 等距圆柱投影 + 抽稀 → SVG |
| `icons.html` / `fetch_icons.py` | Remix Icon 图标库抓取 → 内联 SVG sprite（离线可用） |
| `ne_110m_land.geojson` | Natural Earth 110m 陆地原始数据 |
| `manifest.json` / `sw.js` / `icon-192.png` / `icon-512.png` | PWA 三件套 |

## 本地开发

```bash
# 重新抓取电台数据（可选，已有 stations.js）
python fetch_stations.py

# 重新生成地球地图（可选，已有 globe_map.svg）
python make_globe.py

# 重新抓取图标（可选，已有 icons.html）
python fetch_icons.py

# 构建单文件 index.html
python build.py
```

然后直接双击 `index.html`，或起个静态服务：

```bash
python -m http.server 8899
```

## 说明

- 电台能否出声取决于其流地址是否在线、是否允许跨域播放，个别小众台失联属正常现象，「换一站」即可
- 图标来自 [Remix Icon](https://remixicon.com/)（Apache 2.0），地球轮廓来自 [Natural Earth](https://www.naturalearthdata.com/)（公有领域）
