import os
import sys
import time
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

base_dir = os.path.dirname(os.path.abspath(__file__))
target_url_base = f"file:///{os.path.abspath(os.path.join(base_dir, 'index.html')).replace(os.sep, '/')}"

reveal_final_state = True

for arg in sys.argv[1:]:
    if arg.startswith("http://") or arg.startswith("https://") or arg.startswith("file://"):
        target_url_base = arg
    elif arg == "--initial":
        reveal_final_state = False

output_dir = os.path.join(base_dir, "pdf_slajdy_pojedyncze")
final_pdf_path = os.path.join(base_dir, "prezentacja_chopin.pdf")

os.makedirs(output_dir, exist_ok=True)

print("=" * 65)
print(" AUTOMATYCZNY EKSPORTER SLAJDÓW PDF (STAN OSTATECZNY)")
print("=" * 65)
print(f" Adres bazowy: {target_url_base}")
print(f" Stan ostateczny slajdów (pełna treść): {'WŁĄCZONY' if reveal_final_state else 'WYŁĄCZONY'}")
print(f" Folder na pojedyncze PDF: {output_dir}")
print(f" Plik końcowy scalony: {final_pdf_path}")
print("=" * 65)

# Kod JS do odkrycia pełnej treści slajdu (wszystkich bulletów, kroków, kafelków)
JS_REVEAL_ALL = """
() => {
    const slide = document.querySelector('.slide-container.active');
    if (!slide) return;

    // 1. Odkryj wszystkie bullety w liście (np. slajd 5, 6, 7 itp.)
    slide.querySelectorAll('.feature-list li').forEach(el => {
        el.classList.remove('bullet-dimmed', 'bullet-active');
        el.classList.add('bullet-normal');
    });

    // 2. Odkryj wszystkie kafelki, warstwy i karty
    slide.querySelectorAll('.tile, .layer-card, .stacked-card, .tiled-content .tile').forEach(el => {
        el.classList.remove('tile-dimmed', 'tile-active');
        el.classList.add('tile-normal');
    });

    // 3. Kroki kaskadowe (np. slajd 2)
    slide.querySelectorAll('.m-step').forEach(el => {
        el.classList.remove('step-dimmed');
        el.classList.add('step-normal');
    });

    // 4. Case Study Flow (slajd z przewijaną osią) - włącz widok pełnego podsumowania (tryb 6)
    const caseFlow = slide.querySelector('.case-study-flow');
    if (caseFlow) {
        slide.classList.add('mode-overview');
        const track = slide.querySelector('#caseVTrack');
        if (track) track.style.transform = 'none';
        slide.querySelectorAll('.case-step-card, .case-summary-trigger').forEach(el => {
            el.classList.remove('tile-dimmed', 'tile-active', 'tile-passed');
            el.classList.add('tile-normal');
        });
    }

    // 5. Zdjęcia i mockupy
    slide.querySelectorAll('.image-wrapper').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
    });
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # 1. Załaduj stronę, aby policzyć slajdy
    page.goto(f"{target_url_base}#1", wait_until="networkidle")
    time.sleep(1)
    
    total_slides = page.evaluate("() => document.querySelectorAll('.slide-container').length")
    if not total_slides:
        total_slides = 25
        
    print(f"[INFO] Wykryto {total_slides} slajdów w prezentacji.")
    
    generated_pdfs = []
    
    for i in range(1, total_slides + 1):
        slide_url = f"{target_url_base}#{i}"
        pdf_filename = f"slajd_{i:02d}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # Nawigacja do konkretnego slajdu w przeglądarce
        page.goto(slide_url, wait_until="networkidle")
        time.sleep(0.4)
        
        # Wykrycie czy slajd zawiera sekwencję znikających kroków (np. Case Study z 6 krokami)
        step_dots_count = page.evaluate("""
        () => {
            const slide = document.querySelector('.slide-container.active');
            if (!slide) return 0;
            const dots = slide.querySelectorAll('.case-indicator-dot');
            return dots.length;
        }
        """)

        if step_dots_count > 1:
            print(f" -> [{i:02d}/{total_slides}] Wykryto slajd z sekwencją kroków ({step_dots_count} kroków). Wygenerowano osobne PDF-y dla każdego kroku:")
            for step in range(1, step_dots_count + 1):
                page.evaluate(f"""
                () => {{
                    const slide = document.querySelector('.slide-container.active');
                    if (!slide) return;
                    const dots = slide.querySelectorAll('.case-indicator-dot');
                    if (dots && dots[{step - 1}]) {{
                        dots[{step - 1}].click();
                    }}
                }}
                """)
                time.sleep(0.3)
                
                step_pdf_filename = f"slajd_{i:02d}_krok_{step:02d}.pdf"
                step_pdf_path = os.path.join(output_dir, step_pdf_filename)
                
                page.pdf(
                    path=step_pdf_path,
                    width="1920px",
                    height="1080px",
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
                )
                generated_pdfs.append(step_pdf_path)
                print(f"      - Krok {step:02d}/{step_dots_count:02d}: {step_pdf_filename}")
        else:
            # Standardowy slajd
            if reveal_final_state:
                page.evaluate(JS_REVEAL_ALL)
                time.sleep(0.2)
            
            page.pdf(
                path=pdf_path,
                width="1920px",
                height="1080px",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
            )
            generated_pdfs.append(pdf_path)
            print(f" -> [{i:02d}/{total_slides}] Zapisano stan ostateczny: {pdf_filename}")
        
    browser.close()

print("\n[INFO] Łączenie pojedynczych plików PDF w jeden dokument końcowy...")

writer = PdfWriter()
for pdf in generated_pdfs:
    writer.append(pdf)

actual_final_path = final_pdf_path
try:
    writer.write(actual_final_path)
except PermissionError:
    actual_final_path = os.path.join(base_dir, "prezentacja_chopin_pelna.pdf")
    writer.write(actual_final_path)
    print(f"[UWAGA] Plik prezentacja_chopin.pdf był otwarty w innym programie. Zapisano jako: {actual_final_path}")

writer.close()

size_mb = os.path.getsize(actual_final_path) / (1024 * 1024)
print(f"\n[SUKCES] Wygenerowano:")
print(f" 1. Pojedyncze pliki PDF: {output_dir} (25 plików z pełną treścią)")
print(f" 2. Scalony plik PDF: {actual_final_path} ({size_mb:.2f} MB)")
print("=" * 65)
