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
image_count = 0

# Zbiór przetworzonych xref głównych obrazów (aby uniknąć duplikatów)
processed_xrefs = set()

for page_number in range(len(doc)):
    page = doc[page_number]
    image_list = page.get_images(full=True)
    
    if not image_list:
        continue
    
    for img in image_list:
        xref = img[0]
        smask = img[1]  # xref maski (jeśli >0)
        
        # Pomijamy czystą maskę (zazwyczaj mała lub bez wymiarów)
        if smask > 0 and xref in processed_xrefs:
            continue
        
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image["ext"]
        
        # Jeśli jest maska – komponujemy pełny obraz
        if smask > 0:
            mask_image = doc.extract_image(smask)
            if mask_image:
                pix_base = fitz.Pixmap(image_bytes)
                pix_mask = fitz.Pixmap(mask_image["image"])
                pix_full = fitz.Pixmap(pix_base, pix_mask)  # nakładamy maskę
                image_bytes = pix_full.tobytes("png")  # zapisujemy jako PNG (najlepsza jakość)
                ext = "png"
                pix_full = None
                pix_mask = None
                pix_base = None
            processed_xrefs.add(xref)  # oznaczamy jako przetworzony
        
        image_count += 1
        filename = f"strona{page_number+1:03d}_obraz{image_count:03d}.{ext}"
        file_path = os.path.join(output_dir, filename)
        
        # Obsługa duplikatów (rzadko)
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name_part, ext_part = os.path.splitext(original_path)
            file_path = f"{name_part}_{counter}{ext_part}"
            counter += 1
        
        with open(file_path, "wb") as img_file:
            img_file.write(image_bytes)
        
        print(f"Zapisano: {os.path.basename(file_path)}")

if image_count == 0:
    print("Nie znaleziono żadnych obrazów w PDF.")
else:
    print(f"\nGotowe! Wyodrębniono {image_count} pełnych obrazów do folderu:\n{output_dir}")

input("\nNaciśnij Enter, aby zakończyć...")
