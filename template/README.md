# 🚀 Szablon Dedykowanego Generatora Prezentacji (Presentation Engine Template)

Gotowy, czysty moduł do generowania i tworzenia interaktywnych prezentacji w kodzie HTML/CSS/JS, integrujący automatyczną synchronizację z **Figmą**, komentarze slajdów **Netlify Forms**, eksport do **PDF** oraz automatyczną publikację **GitHub/Netlify**.

---

## 📁 Struktura Projektu

```text
projekt_prezentacji/
├── components/           # Komponenty wielokrotnego użytku (header, controls, komenty)
│   ├── controls.html
│   ├── overview_modal.html
│   ├── comment_modal.html
│   └── header.html
├── slides/               # Poszczególne slajdy (slide_01.html, slide_02.html, itp.)
│   └── slide_01.html
├── styles/
│   └── main.css          # Główny arkusz stylów prezentacji z trybem Ciemnym i Jasnym
├── scripts/
│   ├── presentation_engine.js  # Silnik nawigacji, skróty klawiszowe (← → F O C T)
│   └── sync_figma.py           # Parser API Figmy -> automatyczne tworzenie slajdów HTML
├── build.py              # Kompilator projektu -> buduje scalony index.html + Git push
├── browser_pdf_exporter.py # Generator i scalacz wysokiej jakości plików PDF
└── requirements.txt
```

---

## 🛠️ Jak Uruchomić w Nowym Projekcie:

### 1. Inicjalizacja środowiska Python
```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\playwright.exe install chromium
```

### 2. Kompilacja Prezentacji
Aby scalić komponenty, slajdy i pliki w jeden produkcyjny `index.html`:
```bash
.\.venv\Scripts\python.exe build.py
```

### 3. Synchronizacja z Figmą
1. Otwórz `scripts/sync_figma.py` i wpisz swój token Figma oraz klucz pliku:
   ```python
   FIGMA_TOKEN = "figd_..."
   FILE_KEY = "..."
   ```
2. Uruchom synchronizację:
   ```bash
   .\.venv\Scripts\python.exe scripts/sync_figma.py
   ```
3. Nazwij ramki w Figmie np. `slide_01`, `slide_02`, a skrypt automatycznie odczyta układy, teksty, kolory oraz kształty!

### 4. Generowanie pliku PDF ze slajdów
```bash
.\.venv\Scripts\python.exe browser_pdf_exporter.py
```

---

## ⌨️ Skróty Klawiszowe w Prezentacji:
* **Strzałki / Spacja / Enter** – Przejście do następnego / poprzedniego slajdu
* **O** – Przegląd wszystkich slajdów (Overview Grid)
* **C** – Zostaw uwagę / komentarz do bieżącego slajdu (Netlify Forms)
* **T** – Przełączenie motywu Jasny / Ciemny
* **F** – Tryb pełnoekranowy (Fullscreen)
