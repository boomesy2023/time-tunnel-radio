# -*- coding: utf-8 -*-
"""
把 Natural Earth 110m 陆地轮廓（GeoJSON）转成等距圆柱投影的 SVG 路径，
用于首页「玻璃地球」的自转地图。输出 globe_map.svg（一份 360° 完整地图，
页面里横向平铺两份即可无缝循环自转）。
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "ne_110m_land.geojson")
DST = os.path.join(BASE, "globe_map.svg")

W, H = 360.0, 180.0          # viewBox：1 单位 = 1 度
MIN_AREA = 0.6               # 过滤小岛（平方度）
DEC = 1                      # 坐标小数位

def project(lon, lat):
    return (lon + 180.0, 90.0 - lat)

def area(ring):
    s = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]; x2, y2 = ring[i + 1]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0

def simplify(pts, tol=0.22):
    """道格拉斯-普克抽稀（按度）；闭合环先去掉重复的尾点，否则首尾重合会让算法退化"""
    if pts and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return pts
    def rdp(points):
        if len(points) < 3:
            return points
        x1, y1 = points[0]; x2, y2 = points[-1]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5 or 1e-9
        idx, dmax = 0, -1
        for i in range(1, len(points) - 1):
            px, py = points[i]
            d = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm
            if d > dmax:
                idx, dmax = i, d
        if dmax > tol:
            return rdp(points[:idx + 1])[:-1] + rdp(points[idx:])
        return [points[0], points[-1]]
    return rdp(pts)

def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    subs = []
    kept = 0
    for feat in data["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "Polygon" else [c for mp in geom["coordinates"] for c in mp]
        for ring in polys:
            pts = [(float(x), float(y)) for x, y in ring]
            if area(pts) < MIN_AREA:
                continue
            # 过滤南极洲（球面底部会被裁成横带，观感差）
            if sum(p[1] for p in pts) / len(pts) < -60:
                continue
            pts = simplify(pts)
            if len(pts) < 4:
                continue
            proj = [project(x, y) for x, y in pts]
            kept += 1
            d = "M" + f"{proj[0][0]:.{DEC}f} {proj[0][1]:.{DEC}f}"
            for x, y in proj[1:]:
                d += "L" + f"{x:.{DEC}f} {y:.{DEC}f}"
            subs.append(d + "Z")

    path = "".join(subs)
    svg = (
        '<svg viewBox="0 0 360 180" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#818cf8"/><stop offset="0.55" stop-color="#6366f1"/>'
        '<stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>'
        f'<path fill="url(#lg)" fill-opacity="0.92" stroke="rgba(255,255,255,.55)" '
        f'stroke-width="0.5" stroke-linejoin="round" d="{path}"/></svg>'
    )
    with open(DST, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"陆地多边形 {kept} 个 → {DST}，{len(svg)} 字节")

if __name__ == "__main__":
    main()
