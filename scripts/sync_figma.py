import urllib.request
import json
import os
import sys
import re

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_figma_token():
    token = os.environ.get("FIGMA_TOKEN")
    if token:
        return token
    env_path = os.path.join(base_dir, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("FIGMA_TOKEN="):
                    return line.strip().split("=", 1)[1].strip("\"'")
    return ""

FIGMA_TOKEN = get_figma_token()
FILE_KEY = "SMtTkLZMcJLzJaRvaZS0fc"

# Słownik jawnego mapowania (opcjonalny, domyślnie używa inteligentnego generatora nazw kolorów)
VAR_NAME_MAP = {}

def hex_to_color_name(hex_code):
    hex_clean = hex_code.lower().lstrip('#')
    
    # Dokładne dopasowania najczęstszych kolorów UI
    exact_names = {
        '000000': '--color-black',
        '0d0d0d': '--color-dark-obsidian',
        '171717': '--color-card-dark',
        '1e1e1e': '--color-charcoal',
        'ffffff': '--color-white',
        'f8fafc': '--color-slate-light',
        'b71818': '--color-crimson-red',
        'b61818': '--color-crimson-red',
        'ef4444': '--color-accent-red',
        'fe0467': '--color-chopin-pink',
        'a1a1aa': '--color-muted-gray'
    }
    if hex_clean in exact_names:
        return exact_names[hex_clean]
    
    # Inteligentne wykrywanie odcieni na podstawie RGB
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        
        if r > 200 and g < 80 and b < 80:
            return f"--color-red-{hex_clean}"
        elif r < 80 and g > 200 and b < 80:
            return f"--color-green-{hex_clean}"
        elif r < 80 and g < 80 and b > 200:
            return f"--color-blue-{hex_clean}"
        elif r > 200 and g > 200 and b < 80:
            return f"--color-yellow-{hex_clean}"
        elif r < 60 and g < 60 and b < 60:
            return f"--color-dark-{hex_clean}"
        elif r > 200 and g > 200 and b > 200:
            return f"--color-light-{hex_clean}"
    except Exception:
        pass

    return f"--color-{hex_clean}"

def to_kebab_case(name):
    cleaned = name.replace(':', '-').replace('VariableID-', '')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', cleaned)
    kebab = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    if not kebab.startswith('--'):
        kebab = f"--{kebab}"
    return kebab

def fetch_figma_document():
    url = f"https://api.figma.com/v1/files/{FILE_KEY}?depth=3"
    req = urllib.request.Request(url, headers={"X-Figma-Token": FIGMA_TOKEN})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def hex_color(color_obj):
    if not color_obj:
        return "#ffffff"
    r = round(color_obj.get('r', 1.0) * 255)
    g = round(color_obj.get('g', 1.0) * 255)
    b = round(color_obj.get('b', 1.0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def get_corner_radius(node):
    if 'cornerRadius' in node:
        return f"{node['cornerRadius']}px"
    if 'rectangleCornerRadii' in node:
        radii = node['rectangleCornerRadii']
        return f"{radii[0]}px {radii[1]}px {radii[2]}px {radii[3]}px"
    return "0px"

def get_box_shadow(node):
    effects = node.get('effects', [])
    shadows = []
    for eff in effects:
        if eff.get('visible', True) and eff.get('type') == 'DROP_SHADOW':
            color_obj = eff.get('color', {})
            alpha = color_obj.get('a', 0.25)
            r = int(color_obj.get('r', 0) * 255)
            g = int(color_obj.get('g', 0) * 255)
            b = int(color_obj.get('b', 0) * 255)
            offset = eff.get('offset', {})
            ox = offset.get('x', 0)
            oy = offset.get('y', 0)
            blur = eff.get('radius', 0)
            shadows.append(f"{ox}px {oy}px {blur}px rgba({r}, {g}, {b}, {alpha:.2f})")
    return ", ".join(shadows) if shadows else "none"

collected_figma_vars = {}

def render_node(node, frame_x, frame_y, frame_w, frame_h):
    n_type = node.get('type')
    n_name = node.get('name', '')
    bounds = node.get('absoluteBoundingBox', {})
    
    if not bounds:
        return ""
    
    c_x = round(bounds.get('x', 0) - frame_x, 1)
    c_y = round(bounds.get('y', 0) - frame_y, 1)
    c_w = round(bounds.get('width', 0), 1)
    c_h = round(bounds.get('height', 0), 1)
    
    fills = node.get('fills', [])
    color_hex = "transparent"
    color_css_val = "transparent"

    if fills and fills[0].get('type') == 'SOLID':
        color_hex = hex_color(fills[0].get('color'))
        color_css_val = color_hex
        
        # Wykrywanie podpiętych zmiennych Figma (boundVariables)
        bound_vars = node.get('boundVariables', {}).get('fills', []) or fills[0].get('boundVariables', {}).get('color', None)
        if bound_vars:
            var_info = bound_vars[0] if isinstance(bound_vars, list) else bound_vars
            var_id = var_info.get('id', '')
            if var_id:
                if var_id in VAR_NAME_MAP:
                    var_css_name = to_kebab_case(VAR_NAME_MAP[var_id])
                else:
                    # Generowanie czytelnej nazwy na podstawie odcienia koloru (np. #1e1e1e -> --color-charcoal)
                    var_css_name = hex_to_color_name(color_hex)
                
                collected_figma_vars[var_css_name] = color_hex
                color_css_val = f"var({var_css_name}, {color_hex})"
                print(f"   [ZMIENNA FIGMA] Wykryto dla '{n_name}' ({var_id}): {var_css_name} = {color_hex}", flush=True)

    corner_radius = get_corner_radius(node)
    box_shadow = get_box_shadow(node)

    if n_type == 'RECTANGLE':
        if abs(c_w - frame_w) < 10 and abs(c_h - frame_h) < 10:
            return ""
        
        style_parts = [
            f"position: absolute",
            f"left: {c_x}px",
            f"top: {c_y}px",
            f"width: {c_w}px",
            f"height: {c_h}px",
            f"background-color: {color_css_val}"
        ]
        if corner_radius != "0px":
            style_parts.append(f"border-radius: {corner_radius}")
        if box_shadow != "none":
            style_parts.append(f"box-shadow: {box_shadow}")
        
        style_str = "; ".join(style_parts) + ";"
        return f'        <div class="figma-rect" style="{style_str}"></div>'

    elif n_type == 'TEXT':
        text = node.get('characters', '')
        style = node.get('style', {})
        font_size = style.get('fontSize', 36)
        font_weight = style.get('fontWeight', 700)
        font_family = style.get('fontFamily', 'Asap')
        align = style.get('textAlignHorizontal', 'LEFT').lower()
        
        style_parts = [
            f"position: absolute",
            f"left: {c_x}px",
            f"top: {c_y}px",
            f"width: {c_w}px",
            f"min-height: {c_h}px",
            f"font-family: '{font_family}', sans-serif",
            f"font-size: {font_size}px",
            f"font-weight: {font_weight}",
            f"color: {color_css_val}",
            f"text-align: {align}",
            f"line-height: 1.2"
        ]
        if box_shadow != "none":
            style_parts.append(f"box-shadow: {box_shadow}")
            
        style_str = "; ".join(style_parts) + ";"
        return f'        <div class="figma-text" style="{style_str}">{text}</div>'
    
    return ""

def update_css_variables(vars_dict):
    if not vars_dict:
        return
    css_path = os.path.join(base_dir, "styles", "main.css")
    if not os.path.isfile(css_path):
        return
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    import re
    for var_name, var_val in vars_dict.items():
        pattern = re.compile(rf'({re.escape(var_name)}:\s*)[^;]+;')
        if pattern.search(content):
            content = pattern.sub(rf'\1{var_val};', content)
        else:
            if "/* Automatyczne Zmienne z Figmy */" in content:
                content = content.replace("/* Automatyczne Zmienne z Figmy */", f"/* Automatyczne Zmienne z Figmy */\n    {var_name}: {var_val};")
            else:
                content = content.replace(":root {", f":root {{\n    /* Automatyczne Zmienne z Figmy */\n    {var_name}: {var_val};")

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[CSS] Zaktualizowano zmienne w :root w main.css!", flush=True)

def sync_all_figma_slides():
    print(f"[FIGMA] Pobieranie struktury z Figmy...", flush=True)
    doc_data = fetch_figma_document()
    pages = doc_data['document']['children']
    
    synced_slides = []

    for page in pages:
        for frame in page.get('children', []):
            if frame.get('type') in ['FRAME', 'COMPONENT', 'GROUP']:
                frame_name = frame.get('name', 'slide').strip().replace(' ', '_').lower()
                frame_id = frame.get('id')
                
                f_bounds = frame.get('absoluteBoundingBox', {})
                f_x = f_bounds.get('x', 0)
                f_y = f_bounds.get('y', 0)
                f_w = f_bounds.get('width', 1920)
                f_h = f_bounds.get('height', 1080)

                bg_color_hex = "#0D0D0D"
                fills = frame.get('fills', [])
                if fills and fills[0].get('type') == 'SOLID':
                    bg_color_hex = hex_color(fills[0].get('color'))
                else:
                    for child in frame.get('children', []):
                        if child.get('type') == 'RECTANGLE':
                            cb = child.get('absoluteBoundingBox', {})
                            if abs(cb.get('width', 0) - f_w) < 10 and abs(cb.get('height', 0) - f_h) < 10:
                                cfills = child.get('fills', [])
                                if cfills and cfills[0].get('type') == 'SOLID':
                                    bg_color_hex = hex_color(cfills[0].get('color'))
                                    break
                
                elements_html = []
                for child in frame.get('children', []):
                    html_snippet = render_node(child, f_x, f_y, f_w, f_h)
                    if html_snippet:
                        elements_html.append(html_snippet)
                
                body_content = "\n".join(elements_html) if elements_html else '        <h1 style="color: #ffffff;">Slajd z Figmy</h1>'
                
                slide_html = f"""<!-- SLAJD Z FIGMY ({frame_name} - ID: {frame_id}) -->
<div class="slide-container" id="{frame_name}" style="background-color: {bg_color_hex}; position: relative; width: 1920px; height: 1080px; overflow: hidden;">
{body_content}
</div>
"""
                out_path = os.path.join(base_dir, "slides", f"{frame_name}.html")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(slide_html)
                print(f" -> [SLIDE] Wygenerowano: slides/{frame_name}.html (ID: {frame_id}, elementów: {len(elements_html)})", flush=True)
                synced_slides.append(frame_name)
    
    if collected_figma_vars:
        update_css_variables(collected_figma_vars)
        
    print(f"[FIGMA SUKCES] Przetworzono {len(synced_slides)} slajdów! Wygenerowane zmienne: {list(collected_figma_vars.keys())}", flush=True)
    return synced_slides

if __name__ == "__main__":
    sync_all_figma_slides()
