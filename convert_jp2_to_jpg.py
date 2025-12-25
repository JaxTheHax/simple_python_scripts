import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import subprocess
import sys

# Lista wymaganych bibliotek
REQUIRED_PACKAGES = [
    "pillow",          # do obsługi formatu JPEG2000 (JP2)
    "piexif"           # opcjonalnie, do zachowania metadanych EXIF jeśli są
]

def install_missing_packages():
    """Automatycznie instaluje brakujące biblioteki za pomocą pip"""
    print("Sprawdzanie i instalacja wymaganych bibliotek...")
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.lower().replace("-", "_"))
        except ImportError:
            print(f"Instaluję {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{package} zainstalowany pomyślnie.")
            except subprocess.CalledProcessError:
                print(f"Nie udało się zainstalować {package}. Spróbuj ręcznie: pip install {package}")
                sys.exit(1)

def select_jp2_files():
    """Otwiera okno dialogowe do wyboru wielu plików .jp2"""
    root = tk.Tk()
    root.withdraw()  # ukrywamy główne okno

    print("Wybierz pliki JP2 do konwersji...")
    file_paths = filedialog.askopenfilenames(
        title="Wybierz pliki JP2",
        filetypes=[("JPEG 2000 files", "*.jp2"), ("All files", "*.*")]
    )

    if not file_paths:
        print("Nie wybrano żadnych plików. Kończę działanie.")
        sys.exit(0)

    return list(file_paths)

def create_output_folder():
    """Tworzy podfolder z aktualną datą i czasem w formacie YYYYMMDDHHMMSS"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    folder_name = timestamp
    os.makedirs(folder_name, exist_ok=True)
    print(f"Utworzono folder wyjściowy: {folder_name}")
    return folder_name

def convert_jp2_to_jpg(input_files, output_folder):
    """Konwertuje wszystkie wybrane pliki JP2 na JPG i zapisuje w podfolderze"""
    from PIL import Image

    converted_count = 0

    for file_path in input_files:
        try:
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, f"{name_without_ext}.jpg")

            # Otwieramy obraz JP2
            with Image.open(file_path) as img:
                # Konwertujemy na RGB (jeśli ma tryb inny niż RGB, np. CMYK lub RGBA)
                if img.mode in ("RGBA", "LA", "P"):
                    # Dla obrazów z przezroczystością – białe tło
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Zapisujemy jako JPG z dobrą jakością
                img.save(output_path, "JPEG", quality=95, optimize=True)
            
            print(f"✓ Przekonwertowano: {filename} → {name_without_ext}.jpg")
            converted_count += 1

        except Exception as e:
            print(f"✗ Błąd podczas konwersji {filename}: {e}")

    print(f"\nGotowe! Przekonwertowano {converted_count} z {len(input_files)} plików.")
    print(f"Pliki zapisane w folderze: {output_folder}")

def main():
    print("=== Konwerter JP2 → JPG ===\n")
    
    # 1. Instalacja brakujących bibliotek
    install_missing_packages()
    
    # 2. Wybór plików
    jp2_files = select_jp2_files()
    
    # 3. Utworzenie folderu z timestampem
    output_folder = create_output_folder()
    
    # 4. Konwersja i zapis
    convert_jp2_to_jpg(jp2_files, output_folder)
    
    print("\nNaciśnij Enter, aby zamknąć...")
    input()

if __name__ == "__main__":
    main()
