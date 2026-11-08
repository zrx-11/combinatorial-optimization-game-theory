#!/usr/bin/env python3
"""生成四个「从零推导」单文件 HTML：KaTeX 全内联（含字体），移动端优先。"""
import base64, json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
KATEX = pathlib.Path('/home/user/Doubao/chats/38452368406057730/work/katex')
OUT = ROOT / '从零推导'
OUT.mkdir(exist_ok=True)

# ---------- KaTeX 资源内联 ----------
css = (KATEX / 'katex.min.css').read_text(encoding='utf-8')
faces = re.findall(r'@font-face\s*\{[^}]*\}', css)
new_faces = []
for blk in faces:
    fam = re.search(r'font-family:\s*([^;]+);', blk)
    style = re.search(r'font-style:\s*([^;]+);', blk)
    weight = re.search(r'font-weight:\s*([^;]+);', blk)
    urange = re.search(r'unicode-range:\s*([^;]+);', blk)
    wob = re.findall(r'url\(fonts/([^)]+\.woff2)\)', blk)
    if not wob:
        continue
    data = base64.b64encode((KATEX / 'fonts' / wob[0]).read_bytes()).decode()
    parts = ['@font-face{']
    if fam: parts.append('font-family:%s;' % fam.group(1).strip())
    if style: parts.append('font-style:%s;' % style.group(1).strip())
    if weight: parts.append('font-weight:%s;' % weight.group(1).strip())
    parts.append('src:url(data:font/woff2;base64,%s) format("woff2");' % data)
    if urange: parts.append('unicode-range:%s;' % urange.group(1).strip())
    parts.append('}')
    new_faces.append(''.join(parts))
css_inline = css
for blk, nb in zip(faces, new_faces[:len(faces)]):
    css_inline = css_inline.replace(blk, nb, 1)
# 兜底：清掉任何残留 url(fonts/…)
css_inline = re.sub(r'url\(fonts/[^)]+\)', 'url(data:font/woff2;base64,AA==) format("woff2")', css_inline)

js_inline = (KATEX / 'katex.min.js').read_text(encoding='utf-8')
ar_inline = (KATEX / 'auto-render.min.js').read_text(encoding='utf-8')

assert 'url(fonts/' not in css_inline, '字体仍有残留外链'

# ---------- 模板 ----------
CSS = """
:root{--bg:#fbfaf7;--fg:#1e1c19;--muted:#6b6660;--line:#e2ddd5;--accent:#2f6b5e;--card:#fff}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 font-size:16px;line-height:1.78;-webkit-text-size-adjust:100%}
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;padding:10px 14px;
 background:rgba(251,250,247,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar button{font:inherit;font-size:14px;padding:5px 10px;border:1px solid var(--line);background:var(--card);
 color:var(--fg);border-radius:8px;cursor:pointer}
.topbar .cur{flex:1;font-size:14px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.topbar .arrows{display:flex;gap:6px}
main{max-width:920px;margin:0 auto;padding:18px 16px 80px}
section{display:none}
section.active{display:block}
.breadcrumb{font-size:12.5px;color:var(--muted);letter-spacing:.02em;margin-bottom:6px}
h1{font-size:1.42rem;line-height:1.35;margin:.2em 0 .7em;font-weight:650}
h2{font-size:1.12rem;margin:1.6em 0 .5em;font-weight:650;padding-left:10px;border-left:3px solid var(--accent)}
h3{font-size:1rem;margin:1.2em 0 .4em;font-weight:600}
p{margin:.7em 0}
.lead{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:1em 0}
.formula{overflow-x:auto;overflow-y:hidden;padding:4px 2px;margin:.8em 0}
details{border:1px solid var(--line);border-radius:10px;background:var(--card);padding:10px 14px;margin:.9em 0}
details summary{cursor:pointer;font-weight:600;color:var(--accent);list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"▸ ";color:var(--muted)}
details[open] summary::before{content:"▾ "}
details p{margin:.55em 0}
.chapter-nav{display:flex;justify-content:space-between;gap:12px;margin:2.2em 0 .5em;padding-top:1em;border-top:1px solid var(--line)}
.chapter-nav button{font:inherit;font-size:14px;padding:8px 14px;border:1px solid var(--line);background:var(--card);
 border-radius:9px;cursor:pointer;flex:1;text-align:left}
.chapter-nav button:last-child{text-align:right}
.chapter-nav button:disabled{opacity:.4;cursor:default}
.toc{position:fixed;inset:0 auto 0 0;width:min(78vw,300px);background:var(--card);border-right:1px solid var(--line);
 padding:18px 16px;overflow-y:auto;transform:translateX(-102%);transition:transform .22s ease;z-index:30}
.toc.open{transform:none}
.toc h4{margin:.2em 0 1em;font-size:14px;color:var(--muted);font-weight:600}
.toc a{display:block;padding:9px 8px;border-radius:8px;color:var(--fg);text-decoration:none;font-size:14.5px}
.toc a.here{background:#f0f4f1;color:var(--accent);font-weight:600}
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.28);opacity:0;pointer-events:none;transition:opacity .2s;z-index:25}
.scrim.open{opacity:1;pointer-events:auto}
.katex-display{margin:.5em 0}
table{border-collapse:collapse;width:100%;margin:.9em 0;font-size:14.5px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left}
th{background:#f4f1ec}
.tag{display:inline-block;font-size:12px;padding:1px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted);margin-right:6px}
@media (min-width:760px){body{font-size:17px}main{padding:26px 24px 90px}h1{font-size:1.7rem}.toc{width:300px}}
"""

JS = """
var ORDER=[__ORDER__];
function cur(){var a=document.querySelector('section.active');return a?a.id:ORDER[0];}
function showChapter(id){
  var secs=document.querySelectorAll('section');
  var found=false;
  secs.forEach(function(s){ if(s.id===id){s.classList.add('active');found=true;} else {s.classList.remove('active');}});
  if(!found){id=ORDER[0];document.getElementById(id)&&document.getElementById(id).classList.add('active');}
  var sec=document.getElementById(id);
  var t=sec.querySelector('h1');
  document.getElementById('curTitle').textContent=t?t.textContent:'';
  document.querySelectorAll('.toc a').forEach(function(a){
    a.classList.toggle('here',a.getAttribute('data-go')===id);});
  if(history.replaceState){history.replaceState(null,'','#'+id);}
  window.scrollTo(0,0);
}
document.querySelectorAll('section').forEach(function(sec){
  sec.querySelectorAll('.chapter-nav button').forEach(function(b){
    b.addEventListener('click',function(){ if(b.disabled)return; showChapter(b.getAttribute('data-target')); });
  });
});
document.querySelectorAll('.toc a').forEach(function(a){
  a.addEventListener('click',function(e){e.preventDefault();showChapter(a.getAttribute('data-go'));toggleToc(false);});
});
function toggleToc(open){
  var toc=document.getElementById('toc'),scrim=document.getElementById('scrim');
  var v=(typeof open==='boolean')?open:!toc.classList.contains('open');
  toc.classList.toggle('open',v);scrim.classList.toggle('open',v);
}
document.getElementById('tocBtn').addEventListener('click',function(){toggleToc();});
document.getElementById('scrim').addEventListener('click',function(){toggleToc(false);});
document.getElementById('prevBtn').addEventListener('click',function(){
  var i=ORDER.indexOf(cur()); if(i>0) showChapter(ORDER[i-1]);
});
document.getElementById('nextBtn').addEventListener('click',function(){
  var i=ORDER.indexOf(cur()); if(i<ORDER.length-1) showChapter(ORDER[i+1]);
});
if(location.hash&&ORDER.indexOf(location.hash.slice(1))>=0){showChapter(location.hash.slice(1));}
else{showChapter(ORDER[0]);}
"""


def page(title, subtitle, chapters, footer_note):
    """chapters: list of (id, nav, title, html_body)"""
    n = len(chapters)
    order = [c[0] for c in chapters]
    parts = []
    for i, (sid, nav, h1, body) in enumerate(chapters):
        prev_dis = 'disabled' if i == 0 else ''
        next_dis = 'disabled' if i == n - 1 else ''
        prev_t = chapters[i - 1][0] if i > 0 else sid
        next_t = chapters[i + 1][0] if i < n - 1 else sid
        parts.append(f"""
<section id="{sid}">
  <div class="breadcrumb">从零推导 · {nav} · 第 {i+1} / {n} 章</div>
  <h1>{h1}</h1>
  {body}
  <div class="chapter-nav">
    <button data-target="{prev_t}" {prev_dis}>‹ 上一章</button>
    <button data-target="{next_t}" {next_dis}>下一章 ›</button>
  </div>
</section>""")
    toc = '\n'.join(
        f'      <a href="#{c[0]}" data-go="{c[0]}">{c[2]}</a>' for c in chapters)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 从零推导</title>
<style>{CSS}</style>
<style>{css_inline}</style>
</head>
<body>
<header class="topbar">
  <button id="tocBtn" aria-label="目录">目录</button>
  <span class="cur" id="curTitle"></span>
  <div class="arrows">
    <button id="prevBtn" aria-label="上一章">‹</button>
    <button id="nextBtn" aria-label="下一章">›</button>
  </div>
</header>
<nav class="toc" id="toc">
  <h4>{title}：{subtitle}</h4>
{toc}
</nav>
<div class="scrim" id="scrim"></div>
<main>
{''.join(parts)}
</main>
<script>{js_inline}</script>
<script>{ar_inline}</script>
<script>
renderMathInElement(document.body,{{delimiters:[
  {{left:'$$',right:'$$',display:true}},
  {{left:'$',right:'$',display:false}}
],throwOnError:false}});
</script>
<script>{JS.replace('__ORDER__', json.dumps(order))}</script>
</body>
</html>
"""
    return html
