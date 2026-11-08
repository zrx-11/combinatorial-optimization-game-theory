#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 index.html / 单书伴侣里的 Mermaid 加载改成「本地优先，CDN 兜底」（幂等）。

原因：只挂 jsDelivr CDN，国内网络下 mermaid.min.js 常拉不下来，图区会整片空白
（不报错、不提示，属于静默失败）。本地文件放在站内即可秒开，也用不着联网。
"""
import pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'mermaid.min.js'
MARK = '/* MERMAID_LOCAL_PATCH */'
CDN = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'

# index.html：加载器带 mermaidState 状态机
IDX_OLD = """  const s=document.createElement('script');
  s.src='%s';
  s.onload=()=>{ mermaidState='loaded'; run(); };
  s.onerror=()=>{ mermaidState='failed'; };
  document.head.appendChild(s);""" % CDN

IDX_NEW = """  const s=document.createElement('script');
  %s  s.src='assets/mermaid.min.js';
  s.onload=()=>{ mermaidState='loaded'; run(); };
  s.onerror=()=>{
    const c=document.createElement('script');
    c.src='%s';
    c.onload=()=>{ mermaidState='loaded'; run(); };
    c.onerror=()=>{ mermaidState='failed'; };
    document.head.appendChild(c);
  };
  document.head.appendChild(s);""" % (MARK, CDN)

# 单书伴侣：渲染逻辑内联在 s.onload 里
CMP_OLD = """  const s=document.createElement('script');
  s.src='%s';
  s.onload=()=>{ try{""" % CDN

CMP_NEW = """  const s=document.createElement('script');
  %s  s.src='mermaid.min.js';
  s.onerror=()=>{
    const c=document.createElement('script');
    c.src='%s';
    c.onload=s.onload;
    document.head.appendChild(c);
  };
  s.onload=()=>{ try{""" % (MARK, CDN)


def patch(path, local_src, old, new):
    s = path.read_text(encoding='utf-8')
    if MARK in s:
        print(f'  {path.name}: 已有补丁，跳过')
        return
    if old not in s:
        print(f'  {path.name}: 找不到加载器锚点，跳过')
        return
    path.write_text(s.replace(old, new, 1), encoding='utf-8')
    print(f'  {path.name}: 已改为本地优先（{local_src}）')


if not SRC.exists():
    raise SystemExit('assets/mermaid.min.js 不存在，先下载')

patch(ROOT / 'index.html', 'assets/mermaid.min.js', IDX_OLD, IDX_NEW)

book = ROOT / '01-组合优化与博弈论'
shutil.copy2(SRC, book / 'mermaid.min.js')
patch(book / '组合优化与博弈论学习伴侣.html', 'mermaid.min.js', CMP_OLD, CMP_NEW)
print('完成')
