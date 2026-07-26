#!/usr/bin/env python3
"""Post-build: strip React, inject static sidebar + vanilla JS, responsive layout."""
import glob, re, sys, json, hashlib

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

with open(build_dir.replace('/html', '/site/config.json')) as f:
    config = json.load(f)
pages = config['projects'][0]['pages']
toc = config['projects'][0]['toc']

slug_info = {p['slug']: p.get('title', p['slug']) for p in pages if p.get('slug')}

def file_to_slug(fp):
    if not fp: return None
    name = fp.replace('content/', '').replace('.md', '')
    filename = name.split('/')[-1]
    for slug in slug_info:
        if filename == slug or slug in filename or filename.endswith(slug):
            return slug
    c = re.sub(r'^\d+-', '', filename)
    if c in slug_info: return c
    for slug in slug_info:
        if c == slug: return slug
    return filename

def build_sidebar(items, depth=0):
    html = ''
    for item in items:
        if not isinstance(item, dict): continue
        title = item.get('title', '')
        fp = item.get('file', '')
        children = item.get('children', [])
        if fp and children:
            # Section header with its own page + sub-pages: summary wraps a link
            slug = file_to_slug(fp)
            if not title: title = slug_info.get(slug, slug)
            if slug in ('home',) or fp == 'content/home': title = "Giljae's Digital Garden"
            uid = hashlib.md5((title or str(item)).encode()).hexdigest()[:6]
            html += f'<details open class="sf sf-{depth}"><summary><a href="/{slug}" class="sd sd-{depth}">{title}</a></summary>\n{build_sidebar(children, depth + 1)}</details>\n'
        elif fp:
            # Leaf page (no children)
            slug = file_to_slug(fp)
            if not title: title = slug_info.get(slug, slug)
            if slug in ('home',) or fp == 'content/home': title = "Giljae's Digital Garden"
            html += f'<a href="/{slug}" title="{title}" class="sd sd-{depth}">{title}</a>\n'
        elif children:
            # Section group (no file, only children)
            uid = hashlib.md5((title or str(item)).encode()).hexdigest()[:6]
            html += f'<details open class="sf sf-{depth}"><summary>{title}</summary>\n{build_sidebar(children, depth + 1)}</details>\n'
    return html

sidebar_html = build_sidebar(toc)
print(f'{len(slug_info)} pages, {sidebar_html.count("href=")} sidebar items')

CSS = """<style>
html,body{height:auto!important;overflow:visible!important;scroll-padding:0!important}
/* Desktop */
@media(min-width:768px){
body{display:grid!important;grid-template-columns:260px 1fr!important;transition:grid-template-columns .3s}
body.sidebar-collapsed{grid-template-columns:0 1fr!important}
.myst-top-nav{position:relative!important;grid-column:1/-1!important;padding:0!important}
.myst-top-nav-bar{max-width:none!important;padding:8px 16px!important;gap:8px!important}
.myst-primary-sidebar{position:relative!important;display:block!important;width:260px!important;grid-column:1!important;padding:16px 12px 16px 20px!important;height:auto!important;overflow:visible!important}
body.sidebar-collapsed .myst-primary-sidebar{overflow:hidden!important;padding:0!important;width:0!important}
.myst-primary-sidebar-pointer{display:block!important;height:auto!important;overflow:visible!important}
body.sidebar-collapsed .myst-primary-sidebar-pointer{display:none!important}
.myst-primary-sidebar-nav{overflow:visible!important}
.myst-primary-sidebar-footer{display:none!important}
main.article-grid{display:block!important;grid-column:2!important;padding:24px 32px!important;margin:0!important;max-width:none!important}
article{max-width:900px!important;font-size:1.05rem!important;line-height:1.7!important}
footer.article.footer{grid-column:2!important;margin:0!important;padding:12px 32px!important}
.myst-primary-sidebar-topnav a{display:inline-block!important;margin:2px 4px!important;padding:4px 8px!important;font-size:.9rem!important}
.myst-toc a{font-size:.88rem!important;padding:5px 8px!important}
details.sf{margin:0!important}
details.sf>summary{font-size:.88rem!important;padding:6px 8px!important}
/* Desktop depth tree */
.sd-0{padding-left:8px!important;font-weight:600}
.sd-1{padding-left:32px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd-2{padding-left:50px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd-3{padding-left:68px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sf-0>summary{padding-left:4px!important;font-weight:700}
.sf-1>summary{padding-left:28px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sf-2>summary{padding-left:46px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd{font-size:.85rem!important}
.myst-home-link{margin-left:0!important}
.myst-home-link span{font-size:1.05rem!important}
.myst-fm-block h1{font-size:1.8rem!important}
}
/* Mobile */
@media(max-width:767px){
body{display:block!important}
.myst-top-nav{position:relative!important;padding:6px 10px!important;min-height:auto!important}
.myst-top-nav-bar{gap:2px!important}
.myst-home-link{margin-left:0!important}
.myst-home-link span{font-size:.95rem!important}
.myst-search-bar,.myst-search-text-placeholder,.myst-search-shortcut{display:none!important}
.myst-primary-sidebar{display:none!important}
.myst-sidebar-panel{position:fixed!important;top:0!important;left:0!important;width:85%!important;max-width:320px!important;height:100%!important;z-index:1001!important;background:white!important;overflow-y:auto!important;padding:56px 16px 24px!important;box-shadow:2px 0 12px rgba(0,0,0,.15)!important}
.dark .myst-sidebar-panel{background:#1c1917!important}
.myst-sidebar-close{position:fixed!important;top:10px!important;right:15px!important;z-index:1002!important;background:none!important;border:none!important;font-size:28px!important;cursor:pointer!important;color:#666!important;padding:4px 8px!important;line-height:1!important}
.myst-sidebar-close:hover{color:#000!important}.dark .myst-sidebar-close{color:#999!important}.dark .myst-sidebar-close:hover{color:#fff!important}
.myst-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:999;background:rgba(0,0,0,.3)}
.myst-overlay.show{display:block}
.myst-primary-sidebar-pointer{display:block!important;height:auto!important;overflow:visible!important}
.myst-primary-sidebar-nav{overflow:visible!important}
.myst-primary-sidebar-footer{display:none!important}
.myst-primary-sidebar-topnav a{display:block!important;margin:6px 0!important;padding:8px 12px!important;font-size:.95rem!important}
.myst-toc a{display:block;padding:8px 12px;border-radius:8px;text-decoration:none;color:inherit;font-size:.9rem}
details.sf{margin:4px 0}details.sf>summary{padding:8px 12px!important;font-size:.95rem!important}
/* Mobile depth tree */
.sd-0{padding-left:8px!important;font-weight:600}
.sd-1{padding-left:32px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd-2{padding-left:50px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd-3{padding-left:68px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sf-0>summary{padding-left:4px!important;font-weight:700}
.sf-1>summary{padding-left:28px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sf-2>summary{padding-left:46px!important;border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0 8px 8px 0!important}
.sd{padding:9px 12px!important;font-size:.9rem!important}
main.article-grid{display:block!important;padding:12px 16px!important;margin:0!important;max-width:none!important}
footer.article.footer{display:block!important;padding:12px 16px!important;margin:0!important}
.myst-fm-block{margin-bottom:8px!important}.myst-fm-block h1{font-size:1.3rem!important}article{font-size:.95rem!important}
}
/* Common */
.sticky,.fixed{position:relative!important}.hidden{display:revert!important}.translate-y-6{transform:none!important}.opacity-0{opacity:1!important}
.myst-search-shortcut,.myst-search-shortcut kbd,.myst-search-shortcut div{display:none!important}
.myst-toc a{display:block;padding:6px 8px;border-radius:8px;text-decoration:none;color:inherit;font-size:.9rem}.myst-toc a:hover{background:rgba(0,0,0,.06)}
/* === Tree sidebar === */
/* Root group labels (AI, Notes, Getting Started) */
.sf{cursor:pointer;user-select:none;margin:0;position:relative}
.sf>summary{cursor:pointer;padding:6px 8px;border-radius:8px;font-weight:600;font-size:.9rem;color:#1a56db;list-style:none;user-select:none;position:relative}
.sf>summary::-webkit-details-marker{display:none}
.sf>summary::before{content:"\25B6";display:inline-block;margin-right:6px;font-size:.6rem;transition:transform .2s;opacity:.5}
.sf[open]>summary::before{transform:rotate(90deg)}
.sf>summary:hover{background:rgba(0,0,0,.05)}
/* Root-level group (AI, Notes, Getting Started) - uppercase label */
.sf-0>summary{font-size:.85rem;text-transform:uppercase;letter-spacing:.6px;color:#888!important;font-weight:600}
.dark .sf-0>summary{color:#999!important}
/* Sub-section headers that are also links (architecture-overview, evals-overview) */
.sf>summary>.sd{display:inline!important;padding:0!important;background:none!important;border:none!important;font:inherit!important;color:inherit!important;border-radius:0!important}
.sf>summary>.sd:hover{background:transparent!important}
.sf>summary>.sd::before{display:none!important}
/* Page links */
.sd{display:block;padding:5px 8px;border-radius:8px;text-decoration:none;color:inherit;font-size:.88rem;transition:all .12s;position:relative}
.sd:hover{background:rgba(0,0,0,.06)}
.dark .sd:hover{background:rgba(255,255,255,.08)}
.dark .sf>summary:hover{background:rgba(255,255,255,.08)}
.dark .sf>summary{color:#60a5fa}
.dark .sd{color:#e0e0e0}
/* Active page highlight */
.sd[href$="chapter1"],.sd[href$="architecture-overview"],
.sd[href$="i-model-as-component"]{background:#e8f4fd!important;color:#1a56db!important;font-weight:600}
.dark .sd[href$="chapter1"],.dark .sd[href$="architecture-overview"],
.dark .sd[href$="i-model-as-component"]{background:rgba(26,86,219,.2)!important;color:#60a5fa!important}
/* Tree lines (left border for all nested items) */
.sd-1,.sd-2,.sd-3,.sf-1>summary,.sf-2>summary{border-left:2px solid rgba(0,0,0,.08)!important;border-radius:0!important}
.dark .sd-1,.dark .sd-2,.dark .sd-3,.dark .sf-1>summary,.dark .sf-2>summary{border-left-color:rgba(255,255,255,.1)!important}
</style>"""

JS = """<script>
(function(){
var k="myst:theme",h=document.documentElement,b=document.querySelector(".myst-theme-button");
var s=localStorage.getItem(k)||(window.matchMedia("(prefers-color-scheme:light)").matches?"light":"dark");
h.classList.add(s);
b&&b.addEventListener("click",function(){var n=h.classList.contains("dark")?"light":"dark";h.classList.remove("dark","light");h.classList.add(n);localStorage.setItem(k,n);});
new MutationObserver(function(){var d=h.classList.contains("dark");
document.querySelectorAll(".myst-theme-moon-icon").forEach(function(e){e.style.display=d?"block":"none"});
document.querySelectorAll(".myst-theme-sun-icon").forEach(function(e){e.style.display=d?"none":"block"});}).observe(h,{attributes:true,attributeFilter:["class"]});
(function(){
var btn=document.querySelector(".myst-top-nav-menu-button");
var sidebar=document.querySelector(".myst-primary-sidebar");
if(!btn||!sidebar)return;
var mobile=function(){return window.innerWidth<768;};
// Mobile panel setup
var overlay=document.createElement("div");overlay.className="myst-overlay";document.body.appendChild(overlay);
var panel=document.createElement("div");panel.className="myst-sidebar-panel";
var ptr=sidebar.querySelector(".myst-primary-sidebar-pointer");
if(ptr)panel.innerHTML=ptr.innerHTML;
var closeBtn=document.createElement("button");closeBtn.className="myst-sidebar-close";closeBtn.innerHTML="\\u00D7";
document.body.appendChild(closeBtn);document.body.appendChild(panel);
function openM(){overlay.classList.add("show");panel.style.display="block";closeBtn.style.display="block";document.body.style.overflow="hidden";}
function closeM(){overlay.classList.remove("show");panel.style.display="none";closeBtn.style.display="none";document.body.style.overflow="";}
closeM();
btn.addEventListener("click",function(){
if(mobile()){if(panel.style.display==="none")openM();else closeM();}
else{document.body.classList.toggle("sidebar-collapsed");}
});
overlay.addEventListener("click",closeM);closeBtn.addEventListener("click",closeM);
panel.querySelectorAll("a").forEach(function(a){a.addEventListener("click",closeM);});
document.addEventListener("keydown",function(e){if(e.key==="Escape"){if(mobile())closeM();else document.body.classList.add("sidebar-collapsed");}});
window.addEventListener("resize",function(){if(!mobile())closeM();});
})();
})();
</script>"""

n = 0
for f in html_files:
    with open(f) as fp:
        html = fp.read()
    if '<!--PB-->' in html: continue
    html = re.sub(r'<script type="module" async="">.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'<script>window\.__remixContext\s*=.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    html = re.sub(r'<dialog id="myst-no-css">.*?</dialog>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'href="https://wiki\.giljae\.com/([^"]+)" target="_blank" rel="noopener noreferrer"', r'href="/\1"', html)
    # Fix missing-slash bug: https://wiki.giljae.compath → /path
    html = re.sub(r'href="https://wiki\.giljae\.com([^/"][^"]*)"', r'href="/\1"', html)
    html = html.replace(' style="top:60px"', '')
    html = html.replace('</head>', CSS + '\n</head>', 1)
    # Show hamburger on desktop too
    html = html.replace('class="block xl:hidden"><button class="myst-top-nav-menu-button', 'class="block"><button class="myst-top-nav-menu-button')
    html = html.replace('class="myst-primary-sidebar fixed', 'class="myst-primary-sidebar')
    html = html.replace('hidden z-10"', 'z-10"')
    ts = html.find('<div class="myst-toc w-full px-1 dark:text-white">')
    if ts > 0:
        ne = html.find('</div></nav></div>', ts)
        if ne > 0: html = html[:ts] + f'<div class="myst-toc w-full px-1 dark:text-white">\n{sidebar_html}</div>' + html[ne:]
    html = html.replace('</body>', JS + '\n</body>', 1)
    html = html.replace('<!-- PB -->', '')
    html = re.sub(r'\n{4,}', '\n\n', html)
    with open(f, 'w') as fp: fp.write(html)
    n += 1
print(f'Processed {n} files')
