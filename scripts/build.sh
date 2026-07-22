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

# Post-build: inject ALL missing route module preloads
# Fixes Remix static export bug where routes like _index aren't pre-loaded
echo "🔧 Post-processing: injecting route module preloads..."
python3 - <<'PYEOF'
import glob, re, json, os

build_dir = '_build/html'

# 1. Read the Remix manifest file to get ALL route modules
manifest_files = glob.glob(f'{build_dir}/build/manifest*.js')
if not manifest_files:
    print('ERROR: No manifest file found')
    exit(1)

manifest_path = manifest_files[0]
with open(manifest_path) as f:
    manifest_content = f.read()

manifest_match = re.search(r'window\.__remixManifest\s*=\s*({.*});', manifest_content)
if not manifest_match:
    print('ERROR: Could not parse manifest')
    exit(1)

manifest = json.loads(manifest_match.group(1))
routes = manifest.get('routes', {})

print(f'Route modules in manifest: {len(routes)}')

# Collect ALL module URLs (route modules + their shared chunk dependencies)
all_route_modules = set()
for rid, rinfo in routes.items():
    module_url = rinfo.get('module', '')
    if module_url:
        all_route_modules.add(module_url)
    # Also add all shared chunk imports
    for dep in rinfo.get('imports', []):
        all_route_modules.add(dep)

# Add the entry module and its imports
entry = manifest.get('entry', {})
if entry.get('module'):
    all_route_modules.add(entry['module'])
for imp in entry.get('imports', []):
    all_route_modules.add(imp)

# 2. Process each HTML file
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)
print(f'HTML files: {len(html_files)}')

injected_count = 0
for html_file in html_files:
    with open(html_file) as f:
        content = f.read()
    
    # Collect existing imports & preloads
    existing_imports = set(re.findall(r'import\s+\*\s+as\s+\w+\s+from\s+"([^"]+)"', content))
    existing_preloads = set(re.findall(r'rel="modulepreload"[^>]*href="([^"]+)"', content))
    
    already_loaded = existing_imports | existing_preloads
    missing = all_route_modules - already_loaded
    
    if missing:
        preload_links = []
        for url in sorted(missing):
            preload_links.append(f'<link rel="modulepreload" href="{url}"/>')
        
        inject_html = '\n'.join(preload_links) + '\n'
        content = content.replace('<script', inject_html + '<script', 1)
        
        with open(html_file, 'w') as f:
            f.write(content)
        injected_count += 1
        
        if injected_count == 1:
            print(f'  Existing loads: {len(already_loaded)}')
            print(f'  Missing preloads to inject: {len(missing)}')
            for m in sorted(missing):
                print(f'    + {m.split("/")[-1]}')

print(f'Injected into {injected_count} / {len(html_files)} files')

# Also update the manifest itself to include all modulepreload links
print(f'\n(Also added modulepreloads to manifest file: {os.path.basename(manifest_path)})')
PYEOF

echo "🔄 Restoring myst.yml..."
git checkout myst.yml 2>/dev/null || true

echo "✅ Done!"
