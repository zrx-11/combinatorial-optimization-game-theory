#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Mermaid 图预渲染成内联 SVG，塞进 index.html 与单书伴侣（幂等）。

为什么不再运行时渲染：
- 只挂 jsDelivr CDN，国内网络常常拉不下来，图区整片空白且不报错；
- 改成本地 3.3 MB 的 mermaid.min.js，走 Pages 时大文件被中间代理截断，脚本语法报错，
  window.mermaid 仍是 undefined（script.onerror 不触发），图还是空白。

预渲染后：
- 页面不再加载任何 Mermaid JS，仓库瘦约 6.5 MB；
- 图是静态 SVG，离线、弱网、任意浏览器都能看；
- 深色模式下 SVG 保持浅底，可读但不再跟随主题（已知取舍）。
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = pathlib.Path('/tmp/mm_svg.json')
MARK = '/* MERMAID_PRERENDER_PATCH */'

if not MAP.exists():
    sys.exit('缺少 /tmp/mm_svg.json：先跑离屏渲染收集 SVG')

data = json.loads(MAP.read_text(encoding='utf-8'))
svgs = {}
for src, svg in zip(data['blocks'], data['svgs']):
    if svg:
        svgs[src.strip()] = svg
if not svgs:
    sys.exit('没有任何成功渲染的 SVG')

FN = """function renderMermaid(){
  document.querySelectorAll('.mermaid').forEach(el=>{
    if(el.dataset.rendered) return;
    const src=el.textContent.trim();
    const svg=MERMAID_SVG[src];
    if(svg){ el.innerHTML=svg; el.dataset.rendered='1'; el.classList.add('mermaid-done'); }
    else el.dataset.rendered='0';
  });
}

"""

NEW_FN = MARK + '\nconst MERMAID_SVG=' + json.dumps(svgs, ensure_ascii=False) + ';\n\n' + FN


def patch(path: pathlib.Path, end_marker: str):
    s = path.read_text(encoding='utf-8')
    if MARK in s:
        print(f'  {path.name}: 已预渲染，跳过')
        return
    i = s.find('function renderMermaid(){')
    j = s.find(end_marker)
    if i < 0 or j < 0 or j < i:
        print(f'  {path.name}: 找不到函数边界，跳过')
        return
    s = s[:i] + NEW_FN + s[j:]
    path.write_text(s, encoding='utf-8')
    print(f'  {path.name}: 已写入 {len(svgs)} 张预渲染图')


patch(ROOT / 'index.html', '/* ---------- 主题 ---------- */')
patch(ROOT / '01-组合优化与博弈论/组合优化与博弈论学习伴侣.html', '/* ---------- 深色模式 ---------- */')

for p in [ROOT / 'assets' / 'mermaid.min.js', ROOT / '01-组合优化与博弈论' / 'mermaid.min.js']:
    if p.exists():
        p.unlink()
        print(f'  删除 {p.relative_to(ROOT)}')
d = ROOT / 'assets'
if d.exists() and not any(d.iterdir()):
    d.rmdir()
    print('  删除空目录 assets/')
