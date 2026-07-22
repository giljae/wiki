#!/usr/bin/env python3
"""
Post-build: strip Remix hydration, add vanilla JS replacements for:
- Theme toggle (dark/light mode)
- Sidebar collapsible sections
"""
import glob, re, sys

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

VANILLA_JS = """<script>
(function(){
  // 1. Theme toggle
  (function(){
    var key="myst:theme";
    var html=document.documentElement;
    var btn=document.querySelector(".myst-theme-button");
    var saved=localStorage.getItem(key)||(window.matchMedia("(prefers-color-scheme:light)").matches?"light":"dark");
    html.classList.add(saved);
    btn&&btn.addEventListener("click",function(){
      var next=html.classList.contains("dark")?"light":"dark";
      html.classList.remove("dark","light");
      html.classList.add(next);
      localStorage.setItem(key,next);
    });
  })();
  // 2. Sidebar collapsible
  (function(){
    document.querySelectorAll(".myst-primary-sidebar-toc button").forEach(function(btn){
      btn.addEventListener("click",function(){
        var id=this.getAttribute("aria-controls");
        var target=document.getElementById(id);
        if(!target)return;
        var open=target.getAttribute("data-state")==="open";
        target.setAttribute("data-state",open?"closed":"open");
        this.setAttribute("aria-expanded",!open);
        if(open)target.setAttribute("hidden","");else target.removeAttribute("hidden");
        var svg=this.querySelector("svg");
        if(svg)svg.style.transform=open?"rotate(0deg)":"rotate(90deg)";
      });
    });
    // Open all by default
    document.querySelectorAll(".myst-primary-sidebar-toc [data-state=closed]").forEach(function(c){
      c.setAttribute("data-state","open");
      var btn=c.querySelector("button");
      if(btn){
        btn.setAttribute("aria-expanded","true");
        var svg=btn.querySelector("svg");
        if(svg)svg.style.transform="rotate(90deg)";
      }
      var targetId=c.querySelector("[id]");
      if(targetId){
        var t=document.getElementById(targetId.id);
        if(t){t.removeAttribute("hidden");t.setAttribute("data-state","open");}
      }
    });
  })();
})();
</script>"""

count = 0
for html_file in html_files:
    with open(html_file) as f:
        html = f.read()
    if '<!-- PB -->' in html:
        continue

    # Remove Remix module script
    html = re.sub(r'<script type="module" async="">.*?</script>', '', html, flags=re.DOTALL, count=1)
    # Remove __remixContext
    html = re.sub(r'<script>window\.__remixContext\s*=.*?</script>', '', html, flags=re.DOTALL, count=1)
    # Remove modulepreloads
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    # Remove no-css dialog (error overlay)
    html = re.sub(r'<dialog id="myst-no-css">.*?</dialog>', '', html, flags=re.DOTALL, count=1)
    # Inject vanilla JS
    html = html.replace('</body>', VANILLA_JS + '\n</body>', 1)
    html = html.replace('</head>', '<!-- PB -->\n</head>', 1)
    html = re.sub(r'\n{3,}', '\n\n', html)

    with open(html_file, 'w') as f:
        f.write(html)
    count += 1

print(f'Processed {count} / {len(html_files)} files')
