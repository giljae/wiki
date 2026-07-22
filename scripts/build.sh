#!/bin/bash
# Jupyter Book 빌드 스크립트
set -e

echo "📄 Running page generator..."
python3 scripts/generate-pages.py

YEAR=$(date +%Y)
echo "🔧 Injecting year: $YEAR"

if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/{{ year }}/$YEAR/g" myst.yml
else
  sed -i "s/{{ year }}/$YEAR/g" myst.yml
fi

echo "🏗️  Building Jupyter Book..."
BASE_URL=${BASE_URL:-https://wiki.giljae.com} jupyter-book build --html

# Post-build: inject missing route module preloads into all HTML files
echo "🔧 Post-processing: injecting route module preloads..."
python3 - <<'PYEOF'
import json, glob, re, os

build_dir = '_build/html'
config_file = '_build/site/config.json'

with open(config_file) as f:
    config = json.load(f)

# Build the list of ALL route module URLs from the manifest
project = config.get('projects', [{}])[0]
toc = project.get('toc', [])

# Collect all route module URLs from _build/site/public/
public_dir = '_build/site/public'
route_modules = set()
if os.path.exists(public_dir):
    for f in os.listdir(public_dir):
        if f.endswith('.js'):
            # These are route modules  
            pass
            
# Instead, read the manifest from any HTML file to get exact module URLs
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)
if html_files:
    with open(html_files[0]) as f:
        content = f.read()
    
    manifest_match = re.search(r'window\.__remixManifest=({.*?});', content)
    if manifest_match:
        manifest = json.loads(manifest_match.group(1))
        routes = manifest.get('routes', {})
        
        # Find existing imports in the HTML
        existing_imports = set(re.findall(r'import\s+\*\s+as\s+\w+\s+from\s+"([^"]+)"', content))
        print(f'Existing imports: {len(existing_imports)}')
        for imp in existing_imports:
            print(f'  {imp.split("/")[-1]}')
        
        # Find route modules that are NOT pre-imported
        missing_preloads = []
        for rid, rinfo in routes.items():
            module_url = rinfo.get('module', '')
            if module_url and module_url not in existing_imports:
                missing_preloads.append({
                    'id': rid,
                    'url': module_url,
                    'imports': rinfo.get('imports', [])
                })
        
        print(f'\nMissing preloads: {len(missing_preloads)}')
        for m in missing_preloads:
            print(f'  {m["id"]} -> {m["url"].split("/")[-1]}')
        
        if missing_preloads:
            # Build modulepreload links
            preload_links = []
            for m in missing_preloads:
                preload_links.append(f'<link rel="modulepreload" href="{m["url"]}"/>')
                # Also preload dependencies
                for dep in m.get('imports', []):
                    preload_links.append(f'<link rel="modulepreload" href="{dep}"/>')
            
            # Inject into ALL HTML files
            inject_html = '\n'.join(preload_links) + '\n'
            injected_count = 0
            for html_file in html_files:
                with open(html_file) as f:
                    content = f.read()
                # Only inject if not already injected
                if '<link rel="modulepreload"' not in content:
                    content = content.replace('<script', inject_html + '<script', 1)
                    with open(html_file, 'w') as f:
                        f.write(content)
                    injected_count += 1
            print(f'\nInjected into {injected_count} HTML files')
PYEOF

echo "🔄 Restoring myst.yml..."
git checkout myst.yml 2>/dev/null || true

echo "✅ Done!"
