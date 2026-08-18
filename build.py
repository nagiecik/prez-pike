import os
import glob
import re
import base64
import sys

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


base_dir = os.path.dirname(os.path.abspath(__file__))
output_files = list(set([
    os.path.abspath(os.path.join(base_dir, "..", "prezentacja_chopin.html")),
    r"C:\Users\JakubNagiet\Downloads\prezentacja_chopin.html",
    os.path.join(base_dir, "prezentacja_chopin.html"),
    os.path.join(base_dir, "index.html")
]))

def read_file(rel_path):
    full_path = os.path.join(base_dir, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()

def embed_local_assets(content):
    def replacer(match):
        rel_img_path = match.group(1)
        full_img_path = os.path.join(base_dir, rel_img_path)
        if os.path.isfile(full_img_path):
            ext = os.path.splitext(full_img_path)[1].lower().replace('.', '')
            mime = 'image/png' if ext == 'png' else ('image/jpeg' if ext in ['jpg', 'jpeg'] else 'image/svg+xml')
            with open(full_img_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            return f'src="data:{mime};base64,{b64}"'
        return match.group(0)
    return re.sub(r'src=["\'](assets/[^"\']+)["\']', replacer, content)

def compile_presentation():
    css_content = read_file(os.path.join("styles", "main.css"))
    components = {}
    for c_path in glob.glob(os.path.join(base_dir, "components", "*.html")):
        c_name = os.path.splitext(os.path.basename(c_path))[0]
        with open(c_path, 'r', encoding='utf-8') as f:
            components[c_name] = f.read()

    js_content = read_file(os.path.join("scripts", "presentation_engine.js"))

    # Wstawianie komponentów w komponentach (np. logo w header.html)
    def render_components(content):
        for _ in range(3): # obsługa do 3 poziomów potrawień komponentów
            for c_name, c_html in components.items():
                pattern = f"<!-- COMPONENT: {c_name} -->"
                content = content.replace(pattern, c_html)
        return content

    header_comp = render_components(components.get("header", ""))
    controls_comp = render_components(components.get("controls", ""))
    overview_comp = render_components(components.get("overview_modal", ""))
    comment_comp = render_components(components.get("comment_modal", ""))
    pin_comp = render_components(components.get("pin_system", ""))

    slide_files = sorted(glob.glob(os.path.join(base_dir, "slides", "slide_*.html")))
    slides_html_list = []

    for s_path in slide_files:
        with open(s_path, 'r', encoding='utf-8') as f:
            s_content = render_components(f.read())
            slides_html_list.append(s_content)

    all_slides_html = "\n\n".join(slides_html_list)

    import time
    build_timestamp = time.time()

    html_structure = f"""<!DOCTYPE html>
<!-- BUILD_TIMESTAMP: {build_timestamp} -->
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prezentacja wdrożenia CHOPIN</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Asap:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
{css_content}
    </style>
</head>
<body>

    <!-- Ukryty formularz statyczny dla bota Netlify Forms -->
    <form name="presentation-comments" netlify data-netlify="true" hidden action="/">
        <input type="hidden" name="form-name" value="presentation-comments" />
        <input type="text" name="author" />
        <input type="text" name="slide_number" />
        <input type="text" name="slide_title" />
        <textarea name="comment"></textarea>
    </form>

    <!-- Pasek postępu -->
    <div class="progress-bar-container">
        <div class="progress-bar" id="progressBar"></div>
    </div>

    <!-- Górne Logo Brandowe Klienta -->
{header_comp}

    <!-- Przycisk Boczny Poprzedni -->
    <button class="nav-overlay-btn prev-slide" id="overlayPrevBtn" title="Poprzedni slajd (Strzałka w lewo)">
        <i class="fa-solid fa-chevron-left"></i>
    </button>

    <!-- Przycisk Boczny Następny -->
    <button class="nav-overlay-btn next-slide" id="overlayNextBtn" title="Następny slajd (Strzałka w prawo / Spacja)">
        <i class="fa-solid fa-chevron-right"></i>
    </button>

    <!-- Główny Deck Slajdów -->
    <div class="deck-wrapper">
{all_slides_html}
    </div>

    <!-- Panel Nawigacyjny na Dole -->
{controls_comp}

    <!-- Modal Przeglądu Slajdów -->
{overview_comp}

    <!-- Modal Komentarzy -->
{comment_comp}

    <!-- System Visualnych Pinezek -->
{pin_comp}

    <!-- Logika Prezentacji Interaktywnej oraz Live Reload -->
    <script>
{js_content}
    </script>
</body>
</html>
"""

    html_structure = embed_local_assets(html_structure)

    for target_path in output_files:
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(html_structure)
            print(f"BUILD SUCCESSFUL: Exported to {target_path}", flush=True)
        except Exception as e:
            print(f"BUILD WARNING: Could not export to {target_path}: {e}", flush=True)


import subprocess

def push_to_github():
    try:
        print("\n[GIT] Wysyłanie zaktualizowanego pliku index.html na GitHub (dla Netlify)...", flush=True)
        subprocess.run(["git", "add", "index.html"], check=True, cwd=base_dir)
        subprocess.run(["git", "commit", "-m", "Auto build: update index.html with comment modal and Netlify form"], capture_output=True, cwd=base_dir)
        push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, cwd=base_dir)
        if push_res.returncode == 0:
            print("[GIT SUKCES] Pomyślnie wysełano index.html do GitHub! Netlify automatycznie opublikuje nową wersję w kilka sekund.", flush=True)
        else:
            print(f"[GIT NOTICE] {push_res.stderr.strip() or push_res.stdout.strip()}", flush=True)
    except Exception as e:
        print(f"[GIT WARNING] Wystąpił błąd podczas automatycznego wysyłania do GitHuba: {e}", flush=True)

if __name__ == "__main__":
    compile_presentation()
    # push_to_github() # Paused per user instruction

