#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 index.html 的侧栏加「从零推导」入口（幂等）。

坑：跳转目标必须是相对 index.html 的【目录/文件名】，裸文件名会解析到根目录同名文件，
表现为页面打不开（chrome-error）但按钮存在、控制台无报错。
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'
MARK = '/* DERIV_LINK_PATCH */'

LINKS = [
    ('单纯形法（从零推导）', '从零推导/01-单纯形法.html'),
    ('对偶（从零推导）', '从零推导/02-对偶.html'),
    ('NP-完全（从零推导）', '从零推导/03-NP完全.html'),
    ('Nash 均衡（从零推导）', '从零推导/04-Nash均衡.html'),
]

s = INDEX.read_text(encoding='utf-8')
if MARK in s:
    print('已存在补丁，跳过')
    sys.exit(0)

anchor = "  add('学习路径','#/book/'+cur.book+'/path', cur.page==='path'?'active':'');"
if anchor not in s:
    raise SystemExit('找不到锚点，index.html 结构可能变了')

block = anchor + "\n" + MARK + """
  sec('从零推导');
""" + "\n".join(
    "  add(%r, %r, '');" % (label, href) for label, href in LINKS
) + """

"""
s = s.replace(anchor, block, 1)
INDEX.write_text(s, encoding='utf-8')
print('已插入 %d 个推导页入口' % len(LINKS))
