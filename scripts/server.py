# -*- coding: utf-8 -*-
"""简历实时编辑服务：页面改字直接写回文件。
带两道保险：
  1) 禁用缓存 —— 刷新一定拿到最新文件
  2) 版本校验 —— 页面加载后文件若被改过，拒绝保存并提示刷新，避免互相覆盖
用法： python3 _server.py    浏览器开 http://127.0.0.1:8899/<文件名>
"""
import http.server, socketserver, json, io, os, re, urllib.parse, datetime

PORT = 8899
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(ROOT, '_backups')
os.makedirs(BACKUP, exist_ok=True)


def mtime(path):
    return str(int(os.path.getmtime(path) * 1000))


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass

    def end_headers(self):
        # 永远不缓存，刷新必然拿到最新
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        name = os.path.basename(urllib.parse.unquote(self.path.split('?')[0]))
        path = os.path.join(ROOT, name)
        # 给 HTML 注入当前文件版本号，保存时带回来比对
        if name.endswith('.html') and os.path.isfile(path):
            body = io.open(path, encoding='utf-8').read()
            body = body.replace('</head>',
                                f'<meta name="file-version" content="{mtime(path)}"></head>', 1)
            data = body.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/__save':
            self.send_error(404); return
        n = int(self.headers.get('Content-Length', 0))
        try:
            d = json.loads(self.rfile.read(n).decode('utf-8'))
            name = os.path.basename(urllib.parse.unquote(d['file']))
            path = os.path.join(ROOT, name)
            if not os.path.isfile(path):
                raise FileNotFoundError(name)

            # 版本校验：页面加载后文件被别人改过就拒绝，别互相覆盖
            now = mtime(path)
            if d.get('version') and d['version'] != now:
                self._json(409, {'ok': False, 'stale': True, 'server': now,
                                 'err': '文件已被改动，请刷新页面再编辑'})
                return

            src = io.open(path, encoding='utf-8').read()
            ts = datetime.datetime.now().strftime('%m%d-%H%M%S')
            io.open(os.path.join(BACKUP, f'{ts}-{name}'), 'w', encoding='utf-8').write(src)

            m = re.search(r'(<body>)(.*)(</body>)', src, re.S)
            if not m:
                raise ValueError('找不到 body')
            io.open(path, 'w', encoding='utf-8').write(src[:m.start(2)] + d['body'] + src[m.end(2):])
            self._json(200, {'ok': True, 'version': mtime(path)})
        except Exception as e:
            self._json(500, {'ok': False, 'err': str(e)})


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('127.0.0.1', PORT), H) as s:
    print(f'实时编辑服务 http://127.0.0.1:{PORT}/  （无缓存 + 版本校验，备份在 _backups/）')
    s.serve_forever()
