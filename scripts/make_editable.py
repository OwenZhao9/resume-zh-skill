# -*- coding: utf-8 -*-
"""把静态简历 HTML 转成可在浏览器里直接编辑的版本。"""
import io, sys, re

TOOLBAR = ""

STYLE = '''
<style id="tb-style">
  [contenteditable="true"]:focus { outline:2px solid #6aa9ff; outline-offset:3px; border-radius:2px; }
  @media print { #tb-style { display:none !important; } }
</style>
'''

SCRIPT = '''
<script>
(function(){
  var body = document.body;
  var FILE = decodeURIComponent(location.pathname.split("/").pop());
  var VER  = (document.querySelector('meta[name="file-version"]')||{}).content || "";

  function editable(){
    document.querySelectorAll("header,h2,ul,dl,p,.entry").forEach(function(el){
      el.contentEditable = "true";
    });
  }
  editable();


  var bar = null;
  function warn(msg){
    if (bar) return;
    bar = document.createElement("div");
    bar.textContent = msg + "（点这里刷新）";
    bar.style.cssText = "position:fixed;left:50%;transform:translateX(-50%);top:10px;z-index:10000;"
      + "background:#c0392b;color:#fff;padding:7px 14px;border-radius:6px;cursor:pointer;"
      + "font:13px -apple-system,'PingFang SC',sans-serif;box-shadow:0 3px 14px rgba(0,0,0,.3)";
    bar.onclick = function(){ location.reload(); };
    body.appendChild(bar);
  }

  var timer, stale = false;
  body.addEventListener("input", function(){
    if (stale) return;
    clearTimeout(timer);
    timer = setTimeout(save, 800);
  });

  function save(){
    var c = body.cloneNode(true);
    ["#savedot"].forEach(function(sel){ var e = c.querySelector(sel); if (e) e.remove(); });
    if (bar) { var b = c.querySelector("div[style*='translateX']"); if (b) b.remove(); }
    fetch("/__save", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ file: FILE, body: c.innerHTML, version: VER })
    }).then(function(r){ return r.json().then(function(j){ return {s: r.status, j: j}; }); })
      .then(function(o){
        if (o.s === 409) { stale = true; warn("这份文件在别处被改过，你现在的修改不会保存"); return; }
        if (o.j.ok) { VER = o.j.version; }
      })
      .catch(function(){ });
  }

  window.saveNow = save;
  document.addEventListener("keydown", function(e){
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
  });
})();
</script>
'''

def convert(src, dst):
    s = io.open(src, encoding='utf-8').read()
    # 外链样式改成内联，导出的单文件才不会丢样式
    css = io.open('_style.css', encoding='utf-8').read()
    s = s.replace('<link rel="stylesheet" href="_style.css">',
                  '<style>\n' + css + '\n</style>')
    s = s.replace('</head>', STYLE + '</head>')
    s = s.replace('</body>', SCRIPT + '</body>')
    io.open(dst, 'w', encoding='utf-8').write(s)
    print('生成:', dst)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python3 make_editable.py 简历.html [输出.html]')
        print('不给输出名就在原名后面加 -可编辑')
        raise SystemExit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.replace('.html', '-可编辑.html')
    convert(src, dst)
