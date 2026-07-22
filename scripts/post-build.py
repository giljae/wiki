#!/usr/bin/env python3
"""
Post-build: strip React, inject static sidebar, apply single-scroll layout.
"""
import glob, re, sys, json, hashlib

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

# Read site config
with open(build_dir.replace('/html', '/site/config.json')) as f:
    config = json.load(f)
project = config['projects'][0]
pages = project['pages']
toc = project['toc']

# Build slug -> title map
slug_info = {}
for p in pages:
    if p.get('slug'):
        slug_info[p['slug']] = p.get('title', p['slug'])

def file_to_slug(file_path):
    if not file_path:
        return None
    name = file_path.replace('content/', '').replace('.md', '')
    parts = name.split('/')
    filename = parts[-1]
    if filename in slug_info:
        return filename
    for slug in slug_info:
        if filename.endswith(slug) or slug.endswith(filename):
            return slug
        if slug in filename:
            return slug
    cleaned = re.sub(r'^\d+-', '', filename)
    if cleaned in slug_info:
        return cleaned
    for slug in slug_info:
        if cleaned == slug or slug == cleaned:
            return slug
    return filename

def build_sidebar_items(items, depth=0):
    html = ''
    base_url = ''
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get('title', '')
        file_path = item.get('file', '')
        children = item.get('children', [])
        
        if file_path:
            slug = file_to_slug(file_path)
            if not title:
                title = slug_info.get(slug, slug)
            if slug == 'home' or file_path == 'content/home':
                title = "Giljae's Digital Garden"
            url_path = f'/{slug}' if slug else '#'
            html += f'<a title="{title}" href="{url_path}">{title}</a>\n'
        
        if children:
            uid = hashlib.md5((title or str(item)).encode()).hexdigest()[:8]
            html += f'<details open class="sidebar-folder">\n'
            html += f'<summary>{title}</summary>\n'
            html += build_sidebar_items(children, depth + 1)
            html += '</details>\n'
    return html

sidebar_html = build_sidebar_items(toc)
item_count = sidebar_html.count('href=')
print(f'Loaded {len(pages)} pages, generated {item_count} sidebar items')

LAYOUT_CSS = """
<style>
/* Single scroll layout - override Jupyter Book fixed layout */
html, body { height: auto !important; overflow: visible !important; scroll-padding: 0 !important; }
.myst-top-nav { position: relative !important; top: auto !important; z-index: 10; }
.myst-primary-sidebar { 
  position: relative !important; top: auto !important; 
  height: auto !important; overflow: visible !important;
  display: block !important; max-width: 100% !important;
}
.myst-primary-sidebar-pointer { display: block !important; height: auto !important; overflow: visible !important; }
.myst-primary-sidebar-nav { overflow: visible !important; }
.myst-primary-sidebar-footer { display: none !important; }
main.article-grid { display: block !important; }
article.article-grid { display: block !important; }
.myst-fm-block { padding-top: 0 !important; }
/* Sidebar folder styling */
details.sidebar-folder { margin: 2px 0; }
details.sidebar-folder summary { 
  cursor: pointer; padding: 6px 8px; border-radius: 8px;
  font-weight: 600; font-size: 0.95rem;
  color: #1a56db;
}
details.sidebar-folder summary:hover { background: rgba(0,0,0,0.05); }
details.sidebar-folder a { 
  display: block; padding: 4px 12px 4px 24px; border-radius: 8px;
  text-decoration: none; color: inherit; font-size: 0.9rem;
}
details.sidebar-folder a:hover { background: rgba(0,0,0,0.05); }
/* Nav links in sidebar */
.myst-primary-sidebar-topnav a { display: inline-block; margin: 2px 4px; }
/* Article content */
article { padding: 0 16px; max-width: 900px; margin: 0 auto; }
</style>
"""

VANILLA_JS = """<script>
(function(){
  var k="myst:theme",h=document.documentElement,b=document.querySelector(".myst-theme-button");
  var s=localStorage.getItem(k)||(window.matchMedia("(prefers-color-scheme:light)").matches?"light":"dark");
  h.classList.add(s);
  b&&b.addEventListener("click",function(){
    var n=h.classList.contains("dark")?"light":"dark";
    h.classList.remove("dark","light");h.classList.add(n);localStorage.setItem(k,n);
  });
  // Icon visibility
  !function(){
    var h=document.documentElement;
    new MutationObserver(function(){u();}).observe(h,{attributes:true,attributeFilter:["class"]});
    function u(){var d=h.classList.contains("dark");
      document.querySelectorAll(".myst-theme-moon-icon").forEach(function(e){e.style.display=d?"block":"none";});
      document.querySelectorAll(".myst-theme-sun-icon").forEach(function(e){e.style.display=d?"none":"block";});
    }
    u();
  }();
})();
</script>"""

count = 0
for html_file in html_files:
    with open(html_file) as f:
        html = f.read()
    if '<!-- PB -->' in html:
        continue
    
    # Remove React scripts
    html = re.sub(r'<script type="module" async="">.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'<script>window\.__remixContext\s*=.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    html = re.sub(r'<dialog id="myst-no-css">.*?</dialog>', '', html, flags=re.DOTALL, count=1)
    
    # Fix nav links: remove target=_blank for internal links
    html = re.sub(
        r'href="https://wiki\.giljae\.com/([^"]+)" target="_blank" rel="noopener noreferrer"',
        r'href="/\1"',
        html
    )
    
    # Inject layout CSS before </head>
    html = html.replace('</head>', LAYOUT_CSS + '\n</head>', 1)
    
    # Replace sidebar TOC
    toc_start = html.find('<div class="myst-toc w-full px-1 dark:text-white">')
    if toc_start > 0:
        # Find the end of the sidebar nav (before footer)
        nav_end = html.find('</div></nav></div>', toc_start)
        if nav_end > 0:
            new_toc = f'<div class="myst-toc w-full px-1 dark:text-white">\n{sidebar_html}</div>'
            html = html[:toc_start] + new_toc + html[nav_end:]
    
    html = html.replace('</body>', VANILLA_JS + '\n</body>', 1)
    html = html.replace('<!-- PB -->', '')
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    with open(html_file, 'w') as f:
        f.write(html)
    count += 1

print(f'Processed {count} / {len(html_files)} files')
