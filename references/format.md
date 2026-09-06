# 排版规则：中文简历的具体约束

## 一页是硬上限

超页就压，顺序是：**先砍间距 → 再压措辞 → 最后才动字号**。正文字号不低于 9pt。

一次实测的压缩量：行高 1.44→1.40、字号 9.6→9.4pt、区块标题上间距 7→6px、条目间距 4→3px，一轮就把溢出 5 行压回一页，没删任何内容。

LaTeX 版单靠间距不够时，在**导言区**加，不要改 `.cls`（改了就跟上游分叉）：

```latex
\linespread{0.94}
\setlist[itemize]{topsep=0pt, partopsep=0pt, parsep=0.15ex, itemsep=0pt}
\titlespacing*{\section}{0pt}{*0.5}{*0.25}
\titlespacing*{\subsection}{0pt}{*0.45}{*0.15}
\setlength{\parskip}{0pt}
```

## 不要斜体

中文简历里一律不用斜体。`<em>` 和 `\textit{}` 都不要。

这条踩过：Auto-CV 模板的示例把 `\datedsubsection` 第三段固定写成 `\textit{}`，照抄之后「App Store 已上架」「本科」这类状态词全变斜体，作者原稿里斜体数量是 0。

**推广一条：改格式时只搬结构，不要连带把模板作者的排版趣味搬过来。** 字重、斜体、颜色、大小写是作者的选择，原文没有就不要凭空添。

## 空格

数字与汉字之间、中文与英文之间，都要空格。

```
✓ 11 款产品   76 个词条   1600 余支队伍   共 12 款
✗ 11款产品    另有AI 产业链
```

自检：

```python
re.findall(r'\d[一-鿿]', text)                        # 数字紧贴汉字
re.findall(r'[一-鿿][A-Za-z]|[A-Za-z][一-鿿]', text)   # 中英紧贴
```

## 句末标点统一

所有 bullet 的**句末**要么全带标点，要么全不带，不能混。句子**内部**的逗号、分号、句号照常。

推荐全不带——简历是清单不是文章。

## 冒号对齐

标签长度不一时（「电话」2 字 vs「个人主页」4 字），要让**左边缘和冒号同时对齐**。

用固定宽度 + 两端对齐，不要手打空格：

```css
.contact { display:grid; grid-template-columns:auto auto 1fr auto auto 1fr; }
.contact .lb  { display:inline-block; width:4.6em;
                text-align:justify; text-align-last:justify; }
.contact .cl  { padding-right:2px; }
```

**拉丁字母标签要单独关掉两端对齐**，否则字母被摊开、冒号被推远：

```css
.contact .lb2    { width:3.32em; }              /* 等于 GitHub 的自然宽度 */
.contact .lb2.en { text-align-last:left; }      /* GitHub 不摊开 */
```

盒子宽度要按实测的自然宽度设，别拍脑袋。量法：

```js
const p=document.createElement('span');
p.textContent='GitHub';
p.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;font:'+getComputedStyle(el).font;
document.body.appendChild(p);
p.getBoundingClientRect().width / parseFloat(getComputedStyle(el).fontSize);  // → em
```

## 三级间距

基准值（`--ks = 1` 时）：

```css
h2      { margin:17px 0 4px; }   /* 大项：区块标题 */
.entry  { margin:11px 0 0; }     /* 中项：每段经历 / 每个产品 */
ul      { margin:2px 0 0; }
ul li   { margin-bottom:1.5px; } /* 内部：同一条目下的 bullet */
```

正文 9.8pt / 行高 1.45，行间隙 5.9px。所以三级的比例是 **行间隙 5.9 ： 条目 11 ： 大块 17 ≈ 1 ： 1.9 ： 2.9**。

**规则：条目间距 ≈ 行间隙的 2 倍，大块间距 ≈ 条目间距的 1.5 倍。**

条目间距一旦掉到行间隙的 1.5 倍以下，整页会"融为一体"，看不出哪儿是一条经历的边界——这是实测出来的感受阈值。反过来把条目间距压到 3px、行高拉到 1.55 也不行，条目和正文分不开。

**空间不够时的让步顺序**，从先动到最后动：

1. bullet 之间的 `margin-bottom`（1.5 → 0，只影响多 bullet 的条目）
2. 条目间距（11 → 9，下限 9）
3. 大块间距（17 → 16）
4. 行高（1.45 → 1.44）
5. 字号（最后才动，会引起重新折行，可能反而多出一行）

## 自适应填页（--ks / --kf）

与其每次增删内容都手工调间距，不如把版式交给两个比例变量，页面加载时自己二分求解：

```css
:root { --ks:1; --kf:1; }
body   { font-size: calc(9.8pt * var(--kf)); }
h2     { margin: calc(17px * var(--ks)) 0 calc(4px * var(--ks)); }
.entry { margin: calc(11px * var(--ks)) 0 0; }
ul li  { margin-bottom: calc(1.5px * var(--ks)); }
```

`--ks` 缩放三级间距，`--kf` 缩放全部字号。**三级共用同一个 `--ks`**，所以 1 : 1.9 : 2.9 这个比例永远不走样，缩放只改绝对值。

求解顺序就是上面那张让步表：

1. 字号不动，二分找还放得下的最大 `--ks`
2. `--ks` 到 **0.80**（感知下限）仍放不下 → 改让字号，`--kf` 每档降 0.01，每降一档重新二分 `--ks`
3. `--kf` 降到 0.90 还放不下 → 最后才允许 `--ks` 跌破 0.80
4. 反过来内容太少（`--ks` 顶到 2.20 还余 30px 以上）→ `--kf` 逐档往上放

底部固定留 4px 安全余量。脚本放 `<head>` 里，不要放 `<body>`——可编辑版回写文件时序列化的是 body，放 body 会被存进文件反复叠加。

导出 PDF 时同样生效：Chrome `--print-to-pdf` 会等 `load` 事件，脚本在那之前跑完。

## 所有链接可点

包括邮箱和电话：

```html
<a href="mailto:someone@example.com">someone@example.com</a>
<a href="tel:+8613800138000">13800138000</a>
```

电话带国家码，海外 HR 点了才能直接拨。

**验证要扫 PDF 二进制，不要看 HTML 源码**：

```python
re.findall(rb'(?:https?://|mailto:|tel:)[^\s()<>]{6,120}', open('x.pdf','rb').read())
```

## 所有链接一律右对齐

这是硬约束，写在选择器上，不靠给每个链接手动加 class：

```css
li a.ilink, p.note a.ilink { float:right; margin-left:10px; }
li .rt2 { float:right; margin-left:12px; white-space:nowrap; }  /* 「标签 + URL」整块靠右 */
li .rt2 a.ilink { float:none; margin-left:0; }                  /* 块内的链接不再单独浮动 */
```

三件要注意的：

- **链接前面不要留 `&nbsp;`。** 有人会用一串不换行空格把链接推到右边，改成 float 之后这些空格反而占住行尾，把链接挤到下一行。
- **一行放不下就单独占一行，仍然靠右。** 不要为了挤上去硬删正文。
- **float 放不下会掉到下一行——而下一行可能属于下一条 bullet。** 这时链接看起来像是另一个项目的。末行右侧留够链接宽度 + 10px，或者收几个字。

**数行数时别把 float 算成一行。** float 元素自己的 `top` 跟同行文字的基线盒差一两像素，用 `getClientRects()` 按 top 去重会多数出一行。

## 长网址

一整串不可断的长 URL 会把整行挤走，在上一行末尾留大片空白：

```css
p.line, p.note, li { overflow-wrap:anywhere; }
```

治标。**根治是换短链**——用自己域名做跳转（Cloudflare Pages 的 `public/_redirects` 加一行即可）：

```
/jigsaw   https://play.google.com/store/apps/details?id=very.long.package.name   302
```

88 字符变 26 字符，整段重新排，孤字问题一并消失。

## 项目符号统一

要么全部条目都有 bullet，要么全部没有。混着排会显得某几条是补丁。

## 字体

先查本机实际装了什么，不要凭印象写字体栈。macOS 中文可用的：

| 家族 | 字重 | 类型 |
|---|---|---|
| PingFang SC | Ultralight–Semibold（6 档） | 无衬线 |
| Songti SC | Light / Regular / Bold / Black | 宋体 |
| Heiti SC | Light / Medium | 黑体 |
| Hiragino Sans GB | W3 / W6 | 无衬线 |

PingFang 不在常规字体目录，它是按需下载资源（`/System/Library/AssetsV2/`），`ls /System/Library/Fonts` 找不到但确实可用。

**字体栈里不要写 `-apple-system`。** 屏幕上是 SF Pro，Chrome 导出 PDF 时西文会落到 PingFang 自带的拉丁字形，SF Pro 进不了 PDF——投出去和屏幕上看到的不一样。

姓名字重别设太细。300 在样张上好看，实际打印偏虚，600 更稳。

## 中文简历常见的默认值

页边距 10mm 11mm 8mm、正文 9.4–9.7pt、行高 1.40–1.44、A4 单页。
