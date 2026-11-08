#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 index.html / 单书伴侣里的 Mermaid 加载改成「本地优先，CDN 兜底」（幂等，可升级旧版）。

原因：只挂 jsDelivr CDN，国内网络下拉不下来会整片空白；而本地文件走 gzip 传输时也可能被
中间代理截断，截断的 JS 语法报错后 window.mermaid 是 undefined（element.onerror 不触发）。
所以两条路都要检查 window.mermaid 是否真的就位，坏的走另一条。
"""
import pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'mermaid.min.js'
MARK = '/* MERMAID_LOCAL_PATCH */'
CDN = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'

IDX_OLD = """  const s=document.createElement('script');
  s.src='%s';
  s.onload=()=>{ mermaidState='loaded'; run(); };
  s.onerror=()=>{ mermaidState='failed'; };
  document.head.appendChild(s);""" % CDN

IDX_V1 = """  const s=document.createElement('script');
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

IDX_V2 = """  const s=document.createElement('script');
  %s
  const loadCdn=()=>{
    if(window.mermaid){ mermaidState='loaded'; run(); return; }
    const c=document.createElement('script');
    c.src='%s';
    c.onload=()=>{ if(window.mermaid){ mermaidState='loaded'; run(); } else { mermaidState='failed'; } };
    c.onerror=()=>{ mermaidState='failed'; };
    document.head.appendChild(c);
  };
  s.src='assets/mermaid.min.js';
  s.onload=()=>{ if(window.mermaid){ mermaidState='loaded'; run(); } else { loadCdn(); } };
  s.onerror=loadCdn;
  document.head.appendChild(s);""" % (MARK, CDN)

CMP_OLD = """  const s=document.createElement('script');
  s.src='%s';
  s.onload=()=>{ try{""" % CDN

CMP_V1 = """  const s=document.createElement('script');
  %s  s.src='mermaid.min.js';
  s.onerror=()=>{
    const c=document.createElement('script');
    c.src='%s';
    c.onload=s.onload;
    document.head.appendChild(c);
  };
  s.onload=()=>{ try{""" % (MARK, CDN)

CMP_V2 = """  const s=document.createElement('script');
  %s
  s.src='mermaid.min.js';
  s.onerror=()=>{
    const c=document.createElement('script');
    c.src='%s';
    c.onload=s.onload;
    document.head.appendChild(c);
  };
  s.onload=()=>{ if(!window.mermaid){ s.onerror(); return; } try{""" % (MARK, CDN)


def patch(path, variants, new, label):
    s = path.read_text(encoding='utf-8')
    for idx, old in enumerate(variants):
        if old in s:
            s = s.replace(old, new, 1)
            path.write_text(s, encoding='utf-8')
            kind = '升级旧版补丁' if idx == 0 else '首次打补丁'
            print(f'  {path.name}: {kind}（{label}）')
            return
    print(f'  {path.name}: 已是目标形态或找不到锚点，跳过')


if not SRC.exists():
    raise SystemExit('assets/mermaid.min.js 不存在，先下载')

patch(ROOT / 'index.html', [IDX_V1, IDX_OLD], IDX_V2, 'assets/mermaid.min.js')

book = ROOT / '01-组合优化与博弈论'
shutil.copy2(SRC, book / 'mermaid.min.js')
patch(book / '组合优化与博弈论学习伴侣.html', [CMP_V1, CMP_OLD], CMP_V2, 'mermaid.min.js')
print('完成')
