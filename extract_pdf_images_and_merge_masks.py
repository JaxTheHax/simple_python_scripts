import subprocess
import sys
import os
from datetime import datetime

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Instaluję PyMuPDF...")
    install("pymupdf")
    import fitz

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

print("Otwieram okno wyboru pliku PDF...")
pdf_path = filedialog.askopenfilename(
    title="Wybierz plik PDF",
    filetypes=[("Pliki PDF", "*.pdf"), ("Wszystkie pliki", "*.*")]
)

if not pdf_path:
    print("Nie wybrano pliku. Kończę działanie.")
    sys.exit()

pdf_dir = os.path.dirname(pdf_path)
folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = os.path.join(pdf_dir, folder_name)
os.makedirs(output_dir, exist_ok=True)
print(f"Utworzono folder: {output_dir}")

doc = fitz.open(pdf_path)
page_count = len(doc)
saved_count = 0

# Wysoka rozdzielczość – zoom 2.0 = 200% (300 DPI przy standardowym PDF)
zoom = 2.0
mat = fitz.Matrix(zoom, zoom)

for page_number in range(page_count):
    page = doc[page_number]
    
    # Renderuj stronę do pixmapy (obrazu)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
    
    # Nazwa pliku (raw lub jpg)
    # filename = f"strona{page_number+1:04d}.png"
    filename = f"strona{page_number+1:04d}.jpg"
    file_path = os.path.join(output_dir, filename)
    
    # Zapisz jako PNG (raw lub jpg)
    # pix.save(file_path)
    pix.save(file_path, jpg_quality=95)
    
    saved_count += 1
    print(f"Zapisano: {filename} ({pix.width}x{pix.height} pikseli)")

print(f"\nGotowe! Wyodrębniono {saved_count} stron jako obrazy PNG do folderu:\n{output_dir}")
print("Każdy plik wygląda dokładnie tak, jak strona w PDF-ie (z czarnym tekstem i tłem).")

# input("\nNaciśnij Enter, aby zakończyć...")
