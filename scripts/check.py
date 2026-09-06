#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简历格式自检：空格、句末标点、链接、页数无关的结构问题。

用法： python3 check.py 简历-可编辑.html
"""
import sys, io, re, html
from collections import Counter


def body_text(path):
    s = io.open(path, encoding='utf-8').read()
    i = s.find('<body>')
    b = s[i:] if i >= 0 else s
    b = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', b, flags=re.S)
    return b, html.unescape(re.sub(r'<[^>]+>', ' ', b))


def main(path):
    b, plain = body_text(path)
    bad = 0

    print('=== 空格 ===')
    n1 = sorted(set(re.findall(r'\d[一-鿿]', plain)))
    n2 = sorted(set(re.findall(r'[一-鿿][A-Za-z]|[A-Za-z][一-鿿]', plain)))
    print('  数字紧贴汉字:', n1 or '无'); bad += len(n1)
    print('  中英紧贴:', n2 or '无');     bad += len(n2)

    print('\n=== 句末标点 ===')
    lis = re.findall(r'<li>(.*?)</li>', b, re.S)
    c = Counter()
    for x in lis:
        t = html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
        c['有标点' if t and t[-1] in '。；，、！？' else '无标点'] += 1
    print(f'  {len(lis)} 条 bullet:', dict(c))
    if len(c) > 1:
        print('  ⚠ 句末标点不统一'); bad += 1

    print('\n=== 斜体 ===')
    it = len(re.findall(r'<(em|i)\b', b))
    print('  <em>/<i> 数量:', it, '（中文简历应为 0）')
    bad += it

    print('\n=== 链接 ===')
    linked = re.findall(r'<a[^>]*href="([^"]+)"', b)
    print(f'  可点链接 {len(linked)} 个')
    stripped = re.sub(r'<a[^>]*>.*?</a>', '', b, flags=re.S)
    stripped = html.unescape(re.sub(r'<[^>]+>', ' ', stripped))
    plain_url = set(re.findall(r'https?://[^\s<]+', stripped))
    plain_mail = set(re.findall(r'[\w.+-]+@[\w.-]+\.\w+', stripped))
    for u in sorted(plain_url | plain_mail):
        print('  ⚠ 还是纯文本:', u[:80]); bad += 1
    if not (plain_url or plain_mail):
        print('  没有漏网的纯文本链接')

    print('\n=== 数字一致性（需人工确认）===')
    for m in sorted(set(re.findall(r'(\d+)\s*款', plain))):
        print(f'  出现「{m} 款」')
    print('  ↑ 同一个东西出现两个数就是矛盾')

    print('\n=== 时间线（需人工确认重叠与空档）===')
    for t, d in re.findall(r'<span class="t">(.*?)</span><span class="d">(.*?)</span>', b, re.S):
        t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
        d = html.unescape(re.sub(r'<[^>]+>', '', d)).strip()
        if re.search(r'\d{4}\.\d{2}', d):
            print(f'  {t[:34]:36} {d}')

    print(f'\n{"通过" if bad == 0 else f"{bad} 项需要处理"}')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
