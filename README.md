# 《组合优化与博弈论》点化学习系统 · 部署与使用

## 这是什么

一本教材（谈之奕、林凌《组合优化与博弈论》，浙江大学出版社）被拆成了一套可以按路径学的知识库：8 章零基础精讲、10 篇跨章概念页、18 道章测、27 张抽认卡、56 条术语、1 份速查表，外加 4 个从零推导的单文件交互页面。所有内容收进一个 `index.html`，双击即开，离线可用。

## 目录结构

```
.
├── index.html                      总入口（单文件，统一入口，含全部书内内容）
├── index.md                        Markdown 导航页
├── README.md                       本文件（部署与使用）
├── 交付说明.md                      交付清单、验证结论、取舍说明
├── .nojekyll                       GitHub Pages 关闭 Jekyll
├── 从零推导/                        4 个独立单文件交互页（KaTeX 全内联）
│   ├── 01-单纯形法.html
│   ├── 02-对偶.html
│   ├── 03-NP完全.html
│   └── 04-Nash均衡.html
├── 01-组合优化与博弈论/              单书知识库
│   ├── SKILL.md                    总纲（心智模型、路径、章节索引、前置缺口）
│   ├── chapters/                   8 章精讲
│   ├── concepts/                   10 篇概念页
│   ├── paths/learn.md              学习路径
│   ├── glossary.md / patterns.md / cheatsheet.md / quiz.md / flashcards.md
│   ├── manifest.json               结构化清单（组装 HTML 用）
│   ├── 组合优化与博弈论学习伴侣.html   单书版伴侣，可单独发送
│   └── _work/raw/                  按章合并的 OCR 语料（ch00–ch08）
└── _build/                         生成脚本与验证报告
```

## 怎么用

1. **双击 `index.html`**。左侧是导航（学习路径 / 章节 / 概念 / 测验 / 抽认卡 / 术语 / 模式 / 速查），顶部可搜索全文，进度自动存在浏览器里。
2. 按"学习路径"推进：每章先读精讲，再做章测，错了回对应概念页。
3. 想从零重推核心方法，点侧栏"从零推导"里的四个入口，或直接打开 `从零推导/` 下的 HTML。
4. 只想把一本书发给别人：发 `01-组合优化与博弈论/组合优化与博弈论学习伴侣.html` 就够了。

## 部署到 GitHub Pages

```bash
# 1. 在本目录初始化并推送
git init
git add .
git commit -m "add 组合优化与博弈论 点化学习系统"
git branch -M main
git remote add origin https://github.com/<你的账号>/<仓库名>.git
git push -u origin main

# 2. 仓库 Settings → Pages → Source 选 "Deploy from a branch"
#    Branch 选 main，目录选 / (root)，保存

# 3. 等 1–2 分钟，访问
#    https://<你的账号>.github.io/<仓库名>/
```

注意三件事：

- `.nojekyll` 必须在根目录。它关掉 Jekyll，否则中文目录名与以下划线开头的目录会被跳过。
- 所有链接都是相对路径，仓库名变了也不用改代码。
- 所有关系图在构建时已渲染成静态 SVG 内联在页面里，**不加载任何 Mermaid JS、不依赖 CDN**，断网也能看；代价是深色模式下图仍是浅底，且不再支持主题切换。
- 单个 HTML 约 650 KB（KaTeX 字体全内联），全站约 4.7 MB，远低于 Pages 的 1 GB 上限。

## 验证结论

- `verify_handbook.py`（Playwright + 系统 Chromium）：**17/17 通过**，含首页渲染、9 章首末章渲染、18 道测验作答与解析、卡片翻转与计数、术语过滤、全局搜索、进度跨刷新持久、深色模式、控制台零错误。
- `check_render.py`（390×844 移动端视口）：4 个推导页**逐章全部通过**，无残留 `$`、无横向溢出、面包屑与上下章导航齐全。
- 4 个推导页的 KaTeX 字体已 base64 内联，`url(fonts/…)` 残留为 0，`file://` 下不漏字形。

## 已知限制

- 源 PDF 是扫描件（无文字层），OCR 只用于抓章节结构与定理编号；**书中的公式与数值例子一律用 Python 复算后重写**，不照抄 OCR 结果。
- OCR 仍缺 30 页（PDF 108–135、269–270），对应第 4 章末与第 5 章开头部分、以及参考文献；这部分内容依据目录与上下文补齐，未逐字核对原页。
- 重新生成 `index.html` 后要重跑两个幂等补丁：`_build/patch_deriv_links.py`（加"从零推导"入口）、`_build/patch_mermaid_prerender.py`（把 Mermaid 换成预渲染 SVG）。漏跑第二个，图会退回运行时渲染并依赖 CDN，弱网下可能空白。
- 推导页里的例题是为教学自拟的（如 2×2 博弈、MST 与最短路网络），与原书数字不必一致。
- 教材版权归原出版社与作者，本套材料为学习笔记性质，请勿商用分发。
