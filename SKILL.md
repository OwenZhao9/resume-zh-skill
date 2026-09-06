---
name: resume-zh
description: 改中文简历。把简历做成浏览器里直接编辑、改完自动写回文件的 HTML，同时产出 LaTeX 版和 PDF。包含一套「去 AI 味」的文案规则和中文排版规则，以及一套防止改动互相覆盖的工作流。当用户说「改简历」「简历排版」「简历有 AI 味」「简历转成可编辑的」或要求检查简历格式时使用。
---

# 中文简历改写与排版

这个 skill 解决三件事：**怎么改文案**（去 AI 味）、**怎么排版**（中文简历的具体规则）、**怎么协作**（人在浏览器里改、agent 改文件，两边不打架）。

## 模板来源

LaTeX 版式源自 **[flamingoTOM/Auto-CV](https://github.com/flamingoTOM/Auto-CV)**（178★，基于 LaTeX 的中文简历模板 + `/Auto-CV` Agent Skill）。

本 skill 从它那里继承的是 `resume.cls` 里的宏与版式骨架：

| 宏 | 用途 |
|---|---|
| `\MyName{}` | 大号姓名 |
| `\SimpleEntry{}` | 单行条目 |
| `\section{}` | 一级区块 |
| `\datedsubsection{左}{右}` | 左标题 + 右对齐日期 |
| `\Content{}{}{}` / `\Contenttwo{}{}` | 3 条 / 2 条 bullet |
| `\yourphoto{宽度}` | 右上角证件照，`\smash` 高度为零不占版面 |

**没有继承它的排版趣味。** Auto-CV 的示例把 `\datedsubsection` 第三段固定写成 `\textit{}`，照搬会给中文简历加上不该有的斜体。见 `references/format.md`。

Auto-CV 原仓库是 Windows/MiKTeX 专用（`mpm` / `initexmf` / `winget`），macOS 上要换 TeX Live 的 `tlmgr`，或直接用 TinyTeX（装用户目录，不需要 sudo）。

## 三份规则文档

改任何一句话之前，先读对应那份。

- **`references/voice.md`** —— 文案规则。什么话不能写、为什么假、怎么改。
- **`references/format.md`** —— 排版规则。一页上限、空格、标点、间距、对齐、链接。
- **`references/workflow.md`** —— 协作流程与三个必踩的坑。**动手前必读**，不读会覆盖掉用户的修改。

## 快速上手

```bash
# 1) 从静态 HTML 生成「可编辑版」
python3 scripts/make_editable.py 简历.html

# 2) 起本地服务（页面改动直接写回文件，带版本校验和自动备份）
python3 scripts/server.py

# 3) 浏览器打开 http://127.0.0.1:8899/简历-可编辑.html，点文字直接改

# 4) 随时自检格式
python3 scripts/check.py 简历-可编辑.html
```

导出 PDF：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --no-pdf-header-footer --print-to-pdf=简历.pdf "file://$PWD/简历-可编辑.html"
```

## 一条铁律

**用户在浏览器里改的东西是权威版本。** 改文件之前先读页面，改完之后不要替用户刷新，永远不要清 localStorage、不要重新生成整个可编辑文件。

违反这条会静默抹掉用户几十分钟的修改，而且大概率恢复不了。
