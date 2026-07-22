#!/usr/bin/env python3
"""
Post-build: inject missing Remix route module imports into generated HTML files.
Fixes the --html static export bug where routes/_index isn't pre-imported.
"""
import glob, re, json, sys

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'

# 1. Read the Remix manifest
mlist = glob.glob(f'{build_dir}/build/manifest*.js')
if not mlist:
    print('ERROR: No manifest file found')
    sys.exit(1)

with open(mlist[0]) as f:
    content = f.read()

mm = re.search(r'window\.__remixManifest\s*=\s*({.*});', content)
if not mm:
    print('ERROR: Could not parse manifest')
    sys.exit(1)

manifest = json.loads(mm.group(1))
routes = manifest.get('routes', {})

print(f'Route modules in manifest: {len(routes)}')

# 2. Process each HTML file
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)
injected_count = 0

for html_file in html_files:
    with open(html_file) as f:
        html = f.read()

    # Skip if already processed
    if '<!-- IMPORTS_FIXED -->' in html:
        continue

    # Find existing module imports
    existing_modules = set(re.findall(
        r'import\s+\*\s+as\s+\w+\s+from\s+"([^"]+)"', html
    ))

    # Find the import script block (the one with manifest and route imports)
    script_match = re.search(
        r'(<script type="module" async="">.*?</script>)', html, re.DOTALL
    )
    if not script_match:
        continue

    import_script = script_match.group(1)

    # Determine which route modules are NOT imported
    missing_imports = []
    counter = 2  # route0=root, route1=routes/$, start at route2
    for rid, rinfo in routes.items():
        mod_url = rinfo.get('module', '')
        if mod_url and mod_url not in existing_modules:
            missing_imports.append(
                f'import * as route{counter} from "{mod_url}";'
            )
            counter += 1

    if not missing_imports:
        continue

    # Inject missing imports into the import script block
    new_imports = '\n  '.join(missing_imports)
    new_script = import_script.replace(
        '</script>', f'\n  {new_imports}\n</script>'
    )
    html = html.replace(import_script, new_script)
    html = html.replace('</head>', '<!-- IMPORTS_FIXED -->\n</head>', 1)

    with open(html_file, 'w') as f:
        f.write(html)
    injected_count += 1

    if injected_count == 1:
        print(f'  Already imported: {len(existing_modules)}')
        print(f'  Missing imports to inject: {len(missing_imports)}')
        for imp in missing_imports:
            module_name = imp.split('/')[-1].rstrip('";')
            print(f'    + {module_name}')

print(f'\nInjected into {injected_count} / {len(html_files)} files')
