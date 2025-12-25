import subprocess
import sys
import os
from datetime import datetime

# Funkcja do instalacji brakującej biblioteki
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instalacja pypdf jeśli nie jest dostępna
try:
    from pypdf import PdfReader
except ImportError:
    print("Instaluję bibliotekę pypdf...")
    install("pypdf")
    from pypdf import PdfReader

# Import tkinter (wbudowany w Pythona)
import tkinter as tk
from tkinter import filedialog

# Ukryj główne okno tkinter (potrzebujemy tylko dialogu)
root = tk.Tk()
root.withdraw()

# Otwórz dialog wyboru pliku PDF
print("Otwieram okno wyboru pliku PDF...")
pdf_path = filedialog.askopenfilename(
    title="Wybierz plik PDF",
    filetypes=[("Pliki PDF", "*.pdf"), ("Wszystkie pliki", "*.*")]
)

if not pdf_path:
    print("Nie wybrano pliku. Kończę działanie.")
    sys.exit()

# Katalog pliku PDF
pdf_dir = os.path.dirname(pdf_path)

# Nazwa podfolderu: aktualna data i czas
folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = os.path.join(pdf_dir, folder_name)

# Utwórz podfolder
os.makedirs(output_dir, exist_ok=True)
print(f"Utworzono folder: {output_dir}")

# Otwórz PDF
reader = PdfReader(pdf_path)
image_count = 0

# Przejdź przez wszystkie strony
for page in reader.pages:
    if "/XObject" not in page["/Resources"]:
        continue
    xobjects = page["/Resources"]["/XObject"].get_object()
    
    for obj_name in xobjects:
        obj = xobjects[obj_name].get_object()
        if obj["/Subtype"] == "/Image":
            image_count += 1
            
            # Pobierz dane obrazu
            data = obj._data  # surowe dane binarne
            
            # Określ rozszerzenie (domyślnie .jpg, ale sprawdzamy filtr)
            ext = "jpg"  # większość to JPEG
            if "/Filter" in obj:
                filter_val = obj["/Filter"]
                if filter_val == "/DCTDecode":
                    ext = "jpg"
                elif filter_val == "/JPXDecode":
                    ext = "jp2"
                elif filter_val == "/JBIG2Decode":
                    ext = "jb2g"
                elif filter_val == "/CCITTFaxDecode":
                    ext = "tiff"
                # inne przypadki mogą być png itp., ale rzadko
            
            # Nazwa pliku (użyj oryginalnej jeśli dostępna, inaczej numer)
            base_name = obj_name[1:] + "." + ext  # usuń / z nazwy obiektu
            file_path = os.path.join(output_dir, base_name)
            
            # Jeśli plik istnieje (duplikat nazwy), dodaj numer
            counter = 1
            original_path = file_path
            while os.path.exists(file_path):
                name_part, ext_part = os.path.splitext(original_path)
                file_path = f"{name_part}_{counter}{ext_part}"
                counter += 1
            
            # Zapisz obraz
            with open(file_path, "wb") as img_file:
                img_file.write(data)
            
            print(f"Zapisano: {os.path.basename(file_path)}")

if image_count == 0:
    print("Nie znaleziono żadnych obrazów w PDF.")
else:
    print(f"\nGotowe! Wyodrębniono {image_count} obrazów do folderu:\n{output_dir}")

# Na końcu pokaż komunikat (opcjonalnie)
# input("\nNaciśnij Enter, aby zakończyć...")
