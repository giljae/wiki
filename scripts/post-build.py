#!/usr/bin/env python3
"""
Post-build: strip Remix hydration module script from HTML.
Keeps CSS and non-critical scripts, removes only the module import
and __remixContext that cause the hydration error.
"""
import glob, re, sys

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

stripped_count = 0

for html_file in html_files:
    with open(html_file) as f:
        html = f.read()

    # Remove the module script tag (the last one with imports and __remixRouteModules)
    html = re.sub(
        r'<script type="module" async="">.*?</script>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove __remixContext inline script
    html = re.sub(
        r'<script>window\.__remixContext\s*=.*?</script>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove modulepreload links
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    
    # Clean up multiple blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)

    with open(html_file, 'w') as f:
        f.write(html)
    stripped_count += 1

print(f'Stripped hydration from {stripped_count} / {len(html_files)} files')
