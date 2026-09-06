# resume-zh

改中文简历的 Claude Code / Agent Skill。

把简历做成**在浏览器里直接点着改、改完自动写回文件**的 HTML，同时产出 LaTeX 版和 PDF。除了模板，它主要提供三样东西：一套「去 AI 味」的中文文案规则、一套中文简历排版规则（含自适应填页），以及一套防止人和 agent 互相覆盖改动的工作流。

这些规则不是拍脑袋定的，是一份简历反复改到定稿的过程中一条条试出来的，每条都带实测数字。

## 为什么不用 Word / 在线简历工具

- **一页是硬约束。** Word 里删两个字就要重排一遍，这里由脚本二分求解间距和字号，内容增删之后自己填回一页。
- **改的时候所见即所得，存的时候是纯文本。** 页面上点着改，改动直接写回 HTML 文件，可以 git diff、可以回滚。
- **agent 能改，人也能改，两边不打架。** 服务端做 mtime 版本校验，谁的版本旧了谁被拒绝，不会静默覆盖。

## 安装

```bash
git clone https://github.com/OwenZhao9/resume-zh-skill ~/.claude/skills/resume-zh
```

Claude Code 会自动发现 `~/.claude/skills/` 下的 skill。之后直接说「改简历」「简历排版」「简历有 AI 味」就会触发。

只用脚本、不用 agent 也可以，见下面。

## 怎么用

### 1. 生成可编辑版

```bash
python3 scripts/make_editable.py 简历.html
# 输出 简历-可编辑.html
```

它做三件事：给可编辑元素加 `contenteditable`、把外链 CSS 内联进去、注入存盘脚本。

### 2. 起本地服务

```bash
python3 scripts/server.py          # 默认 127.0.0.1:8899
```

浏览器打开 `http://127.0.0.1:8899/简历-可编辑.html`，点任何一段文字直接改，停手 0.8 秒自动存回文件。每次写入前会在 `_backups/` 留一份带时间戳的备份。

### 3. 自检格式

```bash
python3 scripts/check.py 简历-可编辑.html
```

扫：中英文之间缺空格、句末标点不统一、残留斜体、链接不可点、数字写法、时间线断档。

### 4. 导出 PDF

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --no-pdf-header-footer --print-to-pdf=简历.pdf \
  "http://127.0.0.1:8899/简历-可编辑.html"

pdfinfo 简历.pdf | grep Pages   # 必须是 1
```

走 `http://` 而不是 `file://`——自适应填页的脚本要跑，`file://` 下有些浏览器会拦。

## 内容

| 文件 | 说明 |
|---|---|
| `SKILL.md` | skill 入口，模板来源与快速上手 |
| `references/voice.md` | 文案规则：什么话不能写、为什么假、怎么改 |
| `references/format.md` | 排版规则：一页上限、三级间距、自适应填页、冒号对齐、链接右对齐、空格与标点、字体 |
| `references/workflow.md` | 协作流程与三个必踩的坑 **（动手前必读）** |
| `scripts/server.py` | 本地存盘服务：页面改动写回文件，带版本校验与自动备份 |
| `scripts/make_editable.py` | 从静态 HTML 生成可编辑版 |
| `scripts/check.py` | 格式自检 |
| `templates/style.css` | 简历样式 |
| `templates/*.cls *.sty` | LaTeX 版式，来自 Auto-CV |

## 几条核心规则

完整版见 `references/`，这里列最容易被忽略的：

**三级间距的比例是 1 : 1.9 : 2.9**（行间隙 : 条目 : 大块）。条目间距掉到行间隙的 1.5 倍以下，整页就"融为一体"，看不出哪儿是一条经历的边界。

**空间不够时的让步顺序**：bullet 间距 → 条目间距 → 大块间距 → 行高 → 字号。字号最后动，因为它会引起重新折行，可能反而多出一行。

**不要在字体栈里写 `-apple-system`。** Chrome 导出 PDF 时 SF Pro 不可嵌入，会静默降级，PDF 和屏幕上长得不一样。

**中文简历不要有斜体。** LaTeX 模板里 `\textit{}` 的习惯不要带进来。

**照片不能靠负 margin 顶出页边距。** Chrome 打印会在页面区域边界硬切，实测能切掉 2.3mm。要放大只能向下占版面，或者用 `object-fit: cover` 把照片自带的白边裁掉。

**去 AI 味的重点不是换词，是删掉「元陈述」。** 「产品判断写在作品里：……」这种先给自己的做法贴个抽象标签、再举例证明标签的句子，正常人不会这么说话。删掉标签句，直接说事。

## 一条铁律

**用户在浏览器里改的东西是权威版本。**

改文件之前先读页面，改完之后不要替用户刷新，永远不要清 localStorage、不要重新生成整个可编辑文件。

违反这条会静默抹掉用户几十分钟的修改，而且大概率恢复不了。`references/workflow.md` 里记了三个真实踩过的坑，动手前先读。

## 模板来源

LaTeX 版式源自 [flamingoTOM/Auto-CV](https://github.com/flamingoTOM/Auto-CV)，继承其 `resume.cls` 的宏与骨架，**不继承其排版趣味**（原模板把状态词固定塞进 `\textit{}` 斜体槽）。

原仓库是 Windows/MiKTeX 专用，macOS 用 TeX Live 的 `tlmgr`，或 TinyTeX（装用户目录，不需要 sudo）。

## 许可

模板部分遵循 Auto-CV 上游许可；规则文档与脚本部分 MIT。
