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

def build_sidebar(items):
    html = ''
    for item in items:
        if not isinstance(item, dict): continue
        title = item.get('title', '')
        fp = item.get('file', '')
        children = item.get('children', [])
        if fp:
            slug = file_to_slug(fp)
            if not title: title = slug_info.get(slug, slug)
            if slug in ('home',) or fp == 'content/home': title = "Giljae's Digital Garden"
            html += f'<a href="/{slug}" title="{title}">{title}</a>\n'
        if children:
            uid = hashlib.md5((title or str(item)).encode()).hexdigest()[:6]
            html += f'<details open class="sf"><summary>{title}</summary>\n{build_sidebar(children)}</details>\n'
    return html

sidebar_html = build_sidebar(toc)
print(f'{len(slug_info)} pages, {sidebar_html.count("href=")} sidebar items')

CSS = """<style>
html,body{height:auto!important;overflow:visible!important;scroll-padding:0!important}
/* Desktop: two-column grid */
@media(min-width:768px){
body{display:grid!important;grid-template-columns:260px 1fr!important}
.myst-top-nav{position:relative!important;grid-column:1/-1!important}
.myst-primary-sidebar{position:relative!important;display:block!important;width:260px!important;grid-column:1!important;padding:16px 12px 16px 20px!important;height:auto!important;overflow:visible!important}
.myst-primary-sidebar-pointer{display:block!important;height:auto!important;overflow:visible!important}
.myst-primary-sidebar-nav{overflow:visible!important}
.myst-primary-sidebar-footer{display:none!important}
main.article-grid{display:block!important;grid-column:2!important;padding:20px 32px!important;margin:0!important;max-width:none!important}
footer.article.footer{grid-column:2!important;margin:0!important;padding:12px 32px!important}
.myst-primary-sidebar-topnav a{display:inline-block!important;margin:2px 4px!important;padding:4px 8px!important}
}
/* Mobile: single column */
@media(max-width:767px){
body{display:block!important}
.myst-top-nav{position:relative!important;padding:6px 10px!important;min-height:auto!important}
.myst-top-nav-bar{gap:2px!important}
.myst-home-link{margin-left:0!important}
.myst-home-link span{font-size:.95rem!important}
.myst-search-bar,.myst-search-text-placeholder,.myst-search-shortcut{display:none!important}
/* Sidebar hidden by default, shown via hamburger */
.myst-primary-sidebar{display:none!important}
.myst-primary-sidebar.open{display:block!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;z-index:1000!important;background:transparent!important;overflow:hidden!important;padding:0!important}
.dark .myst-primary-sidebar.open{background:transparent!important}
/* Sidebar panel (the actual nav) */
.myst-sidebar-panel{position:fixed!important;top:0!important;left:0!important;width:85%!important;max-width:320px!important;height:100%!important;z-index:1001!important;background:white!important;overflow-y:auto!important;padding:56px 16px 24px!important;box-shadow:2px 0 12px rgba(0,0,0,.15)!important}
.dark .myst-sidebar-panel{background:#1c1917!important}
/* Close button in sidebar */
.myst-sidebar-close{position:fixed!important;top:10px!important;right:15px!important;z-index:1002!important;background:none!important;border:none!important;font-size:28px!important;cursor:pointer!important;color:#666!important;padding:4px 8px!important;line-height:1!important}
.myst-sidebar-close:hover{color:#000!important}
.dark .myst-sidebar-close{color:#999!important}
.dark .myst-sidebar-close:hover{color:#fff!important}
/* Overlay background */
.myst-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:999;background:rgba(0,0,0,.3)}
.myst-overlay.show{display:block}
.myst-primary-sidebar-pointer{display:block!important;height:auto!important;overflow:visible!important}
.myst-primary-sidebar-nav{overflow:visible!important}
.myst-primary-sidebar-footer{display:none!important}
.myst-primary-sidebar-topnav a{display:block!important;margin:6px 0!important;padding:8px 12px!important;font-size:.95rem!important}
.myst-toc a{display:block;padding:8px 12px;border-radius:8px;text-decoration:none;color:inherit;font-size:.9rem}
details.sf{margin:4px 0}
details.sf>summary{padding:8px 12px!important;font-size:.95rem!important}
details.sf a{padding-left:28px!important}
main.article-grid{display:block!important;padding:12px 16px!important;margin:0!important;max-width:none!important}
footer.article.footer{display:block!important;padding:12px 16px!important;margin:0!important}
.myst-fm-block{margin-bottom:8px!important}
.myst-fm-block h1{font-size:1.3rem!important}
article{font-size:.95rem!important}
}
/* Common: fix sticky/hidden */
.sticky,.fixed{position:relative!important}.hidden{display:revert!important}.translate-y-6{transform:none!important}.opacity-0{opacity:1!important}
.myst-toc a{display:block;padding:6px 8px;border-radius:8px;text-decoration:none;color:inherit;font-size:.9rem}.myst-toc a:hover{background:rgba(0,0,0,.06)}
details.sf{margin:2px 0}details.sf>summary{cursor:pointer;padding:6px 8px;border-radius:8px;font-weight:600;font-size:.9rem;color:#1a56db;list-style:none;user-select:none}
details.sf>summary::-webkit-details-marker{display:none}
details.sf>summary::before{content:"\\25B6";display:inline-block;margin-right:6px;font-size:.7rem;transition:transform .2s}
details.sf[open]>summary::before{transform:rotate(90deg)}
details.sf>summary:hover{background:rgba(0,0,0,.06)}
details.sf a{padding-left:24px!important}
.dark .myst-toc a:hover{background:rgba(255,255,255,.1)}
.dark details.sf>summary:hover{background:rgba(255,255,255,.1)}
.dark details.sf>summary{color:#60a5fa}
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
// Hamburger menu toggle
(function(){
var btn=document.querySelector(".myst-top-nav-menu-button");
var sidebar=document.querySelector(".myst-primary-sidebar");
if(!btn||!sidebar)return;
// Create overlay
var overlay=document.createElement("div");
overlay.className="myst-overlay";
document.body.appendChild(overlay);
// Create sidebar panel (clone sidebar content into it)
var panel=document.createElement("div");
panel.className="myst-sidebar-panel";
var pointer=sidebar.querySelector(".myst-primary-sidebar-pointer");
if(pointer)panel.innerHTML=pointer.innerHTML;
// Create close button
var closeBtn=document.createElement("button");
closeBtn.className="myst-sidebar-close";
closeBtn.innerHTML="\u00D7";
document.body.appendChild(closeBtn);
document.body.appendChild(panel);
function open(){overlay.classList.add("show");panel.style.display="block";closeBtn.style.display="block";document.body.style.overflow="hidden";}
function close(){overlay.classList.remove("show");panel.style.display="none";closeBtn.style.display="none";document.body.style.overflow="";}
close();
btn.addEventListener("click",function(){if(panel.style.display==="none")open();else close();});
overlay.addEventListener("click",close);
closeBtn.addEventListener("click",close);
panel.querySelectorAll("a").forEach(function(a){a.addEventListener("click",close);});
// Escape key
document.addEventListener("keydown",function(e){if(e.key==="Escape")close();});
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
    html = html.replace(' style="top:60px"', '')
    html = html.replace('class="myst-primary-sidebar fixed', 'class="myst-primary-sidebar')
    html = html.replace('hidden z-10"', 'z-10"')
    html = html.replace('</head>', CSS + '\n</head>', 1)
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
