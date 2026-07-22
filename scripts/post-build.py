#!/usr/bin/env python3
"""
Post-build: strip React hydration, inject static sidebar + vanilla JS.
"""
import glob, re, sys, json, hashlib

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

# Read site config
config_path = build_dir.replace('/html', '/site/config.json')
with open(config_path) as f:
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
    """Convert TOC file path to page slug."""
    if not file_path:
        return None
    # Remove content/ prefix and .md extension
    name = file_path.replace('content/', '').replace('.md', '')
    # Extract filename (last part of path)
    parts = name.split('/')
    filename = parts[-1]
    
    # Direct match
    if filename in slug_info:
        return filename
    
    # Try matching by ending (for numeric prefixes like 01-role -> role)
    for slug in slug_info:
        if filename.endswith(slug) or slug.endswith(filename):
            return slug
        # Check if slug is contained in filename (01-role contains 'role')
        if slug in filename:
            return slug
    
    # Try partial match: remove numeric prefix (01-role -> role)
    import re as re2
    cleaned = re2.sub(r'^\d+-', '', filename)
    if cleaned in slug_info:
        return cleaned
    for slug in slug_info:
        if cleaned == slug or slug == cleaned:
            return slug
    
    return filename

def build_sidebar_items(items, depth=0):
    html = ''
    base_url = 'https://wiki.giljae.com'
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
            # Fix root page title
            if slug == 'home' or file_path == 'content/home':
                title = "Giljae's Digital Garden"
            url_path = f'/{slug}' if slug else '#'
            html += f'<a title="{title}" class="block break-words focus:outline outline-blue-200 outline-2 rounded myst-toc-item p-2 my-1 rounded-lg hover:bg-slate-300/30" href="{base_url}{url_path}">{title}</a>\n'
        
        if children:
            uid = hashlib.md5((title or str(item)).encode()).hexdigest()[:8]
            html += f'<div data-state="open" class="w-full">\n'
            html += f'<div class="myst-toc-item flex flex-row w-full gap-2 pl-2 my-1 text-left rounded-lg outline-none hover:bg-slate-300/30">\n'
            html += f'<div title="{title}" class="block break-words rounded py-2 grow cursor-pointer">{title}</div>\n'
            html += f'<button class="self-stretch flex items-center flex-none px-1 rounded-l-md group hover:bg-slate-300/30" aria-label="Open Folder" type="button" aria-controls="sid-{uid}" aria-expanded="true" data-state="open">\n'
            html += f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" data-slot="icon" class="transition-transform duration-300 text-text-slate-700 dark:text-slate-100" height="1.5rem" width="1.5rem" style="transform:rotate(90deg)">\n'
            html += f'<path fill-rule="evenodd" d="M16.28 11.47a.75.75 0 0 1 0 1.06l-7.5 7.5a.75.75 0 0 1-1.06-1.06L14.69 12 7.72 5.03a.75.75 0 0 1 1.06-1.06l7.5 7.5Z" clip-rule="evenodd"/></svg>\n'
            html += f'</button>\n</div>\n'
            html += f'<div data-state="open" id="sid-{uid}" class="pl-3 pr-[2px] collapsible-content">\n'
            html += build_sidebar_items(children, depth + 1)
            html += '</div>\n</div>\n'
    return html

sidebar_html = build_sidebar_items(toc)
item_count = sidebar_html.count('myst-toc-item')
print(f'Loaded {len(pages)} pages from config')
print(f'Generated sidebar with {item_count} items')

# Also print the generated sidebar for debugging
if item_count < 10:
    print('DEBUG - full sidebar HTML:')
    print(sidebar_html[:1000])

VANILLA_JS = """<script>
(function(){
  var k="myst:theme",h=document.documentElement,b=document.querySelector(".myst-theme-button");
  var s=localStorage.getItem(k)||(window.matchMedia("(prefers-color-scheme:light)").matches?"light":"dark");
  h.classList.add(s);
  b&&b.addEventListener("click",function(){
    var n=h.classList.contains("dark")?"light":"dark";
    h.classList.remove("dark","light");h.classList.add(n);localStorage.setItem(k,n);
  });
  !function(){
    function t(el){
      var btn=el.tagName==="BUTTON"?el:el.parentElement.querySelector("button");
      if(!btn)return;
      var id=btn.getAttribute("aria-controls"),target=document.getElementById(id);
      if(!target)return;
      var o=target.getAttribute("data-state")==="open";
      target.setAttribute("data-state",o?"closed":"open");
      btn.setAttribute("aria-expanded",!o);
      if(o)target.setAttribute("hidden","");else target.removeAttribute("hidden");
      var s=btn.querySelector("svg");if(s)s.style.transform=o?"rotate(0deg)":"rotate(90deg)";
    }
    document.querySelectorAll(".myst-primary-sidebar-toc .myst-toc-item").forEach(function(r){
      var btn=r.querySelector("button"),tl=r.querySelector("div[title]");
      if(btn)btn.addEventListener("click",function(){t(this);});
      if(tl)tl.addEventListener("click",function(){t(this);});
    });
  }();
  !function(){
    var h=document.documentElement;
    new MutationObserver(function(){update();}).observe(h,{attributes:true,attributeFilter:["class"]});
    function update(){
      var d=h.classList.contains("dark");
      document.querySelectorAll(".myst-theme-moon-icon").forEach(function(e){e.style.display=d?"block":"none";});
      document.querySelectorAll(".myst-theme-sun-icon").forEach(function(e){e.style.display=d?"none":"block";});
    }
    update();
  }();
})();
</script>"""

count = 0
for html_file in html_files:
    with open(html_file) as f:
        html = f.read()
    if '<!-- PB -->' in html:
        continue
    
    html = re.sub(r'<script type="module" async="">.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'<script>window\.__remixContext\s*=.*?</script>', '', html, flags=re.DOTALL, count=1)
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    html = re.sub(r'<dialog id="myst-no-css">.*?</dialog>', '', html, flags=re.DOTALL, count=1)
    
    # Replace sidebar TOC with generated version
    toc_start = html.find('<div class="myst-toc w-full px-1 dark:text-white">')
    toc_end = html.find('</div></nav></div><div class="myst-primary-sidebar-footer', toc_start)
    if toc_start > 0 and toc_end > 0:
        new_toc = f'<div class="myst-toc w-full px-1 dark:text-white">\n{sidebar_html}</div>'
        html = html[:toc_start] + new_toc + html[toc_end:]
    
    html = html.replace('</body>', VANILLA_JS + '\n</body>', 1)
    html = html.replace('</head>', '<!-- PB -->\n</head>', 1)
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    with open(html_file, 'w') as f:
        f.write(html)
    count += 1

print(f'Processed {count} / {len(html_files)} files')
