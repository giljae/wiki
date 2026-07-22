#!/usr/bin/env python3
"""
Post-build: strip Remix hydration, replace theme toggle with vanilla JS.
"""
import glob, re, sys

build_dir = sys.argv[1] if len(sys.argv) > 1 else '_build/html'
html_files = glob.glob(f'{build_dir}/**/index.html', recursive=True)

# Vanilla JS snippet for theme toggle (injects right before </body>)
THEME_SCRIPT = """
<script>
// Theme toggle - vanilla JS replacement for React hydration
(function() {
  var key = "myst:theme";
  var html = document.documentElement;
  var toggleBtn = document.querySelector(".myst-theme-button");
  
  // Apply saved theme
  var saved = localStorage.getItem(key);
  if (!saved) {
    saved = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  html.classList.add(saved);
  
  // Toggle handler
  if (toggleBtn) {
    toggleBtn.addEventListener("click", function() {
      var current = html.classList.contains("dark") ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      html.classList.remove("dark", "light");
      html.classList.add(next);
      localStorage.setItem(key, next);
    });
  }
})();
</script>
"""

stripped_count = 0

for html_file in html_files:
    with open(html_file) as f:
        html = f.read()

    # Skip if already processed
    if '<!-- POST_BUILD_DONE -->' in html:
        continue

    # 1. Keep theme CSS - don't touch stylesheets
    
    # 2. Remove the Remix module script (the one with imports)
    html = re.sub(
        r'<script type="module" async="">.*?</script>',
        '',
        html,
        flags=re.DOTALL,
        count=1
    )
    
    # 3. Remove __remixContext script
    html = re.sub(
        r'<script>window\.__remixContext\s*=.*?</script>',
        '',
        html,
        flags=re.DOTALL,
        count=1
    )
    
    # 4. Remove modulepreload links
    html = re.sub(r'\n\s*<link rel="modulepreload"[^>]*/>', '', html)
    
    # 5. Remove the React error boundary that hides content
    #    (the "Application Error" overlay)
    html = re.sub(
        r'<dialog id="myst-no-css">.*?</dialog>',
        '',
        html,
        flags=re.DOTALL,
        count=1
    )
    
    # 6. Keep the initial theme script (reads localStorage and sets class)
    #    but remove the duplicate one that references myst:theme
    
    # 7. Inject vanilla theme toggle before </body>
    html = html.replace('</body>', THEME_SCRIPT + '\n</body>', 1)
    
    # Mark as done
    html = html.replace('</head>', '<!-- POST_BUILD_DONE -->\n</head>', 1)
    
    # Clean up excessive blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    with open(html_file, 'w') as f:
        f.write(html)
    stripped_count += 1

print(f'Processed {stripped_count} / {len(html_files)} files with theme toggle injected')
