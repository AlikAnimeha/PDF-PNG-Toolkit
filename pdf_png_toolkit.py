# PDF ↔ PNG Toolkit
# Автор: AlikAnimeha (Marko)
# GitHub: https://github.com/AlikAnimeha/PDF-PNG-Toolkit

import os
import glob
from pdf2image import convert_from_path
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

# ====================================================================
# Настройка Poppler (только для Windows)
POPPLER_PATH = r'C:\poppler\Library\bin'
# ====================================================================

def convert_pdfs_to_png(poppler_path):
    current_dir = Path.cwd()
    pdf_input_dir = current_dir / "PDF_Files"
    png_output_dir = current_dir / "PNG_Output"

    pdf_input_dir.mkdir(exist_ok=True)
    png_output_dir.mkdir(exist_ok=True)
    print(f"✅ Папка для PDF: {pdf_input_dir}")
    print(f"✅ Папка для PNG: {png_output_dir}")

    pdf_files = list(pdf_input_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ В папке PDF_Files нет PDF-файлов.")
        print("➡️  Поместите PDF-файлы в папку PDF_Files и запустите режим 1 снова.")
        return

    for pdf_path in pdf_files:
        pdf_name = pdf_path.stem

        if list(png_output_dir.glob(f"{pdf_name}_page_*.png")):
            print(f"⏭️  Пропускаем: {pdf_path.name}")
            continue

        print(f"\n▶️ Обработка: {pdf_path.name}")
        try:
            pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
            for i, page in enumerate(pages):
                png_filename = f"{pdf_name}_page_{i+1}.png"
                page.save(png_output_dir / png_filename, 'PNG')
            print(f"✅ Готово: {pdf_path.name}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue


def combine_png_to_pdf():
    current_dir = Path.cwd()

    default_folder = "PNG_Output"
    print(f"\n📂 Режим объединения PNG в PDF")
    print(f"По умолчанию используется папка: '{default_folder}'")
    user_folder = input(f"Нажмите Enter для выбора по умолчанию, или введите имя другой папки: ").strip()

    input_folder = current_dir / (user_folder if user_folder else default_folder)

    if not input_folder.exists():
        print(f"❌ Папка не найдена: {input_folder}")
        return

    png_files = sorted(input_folder.glob("*.png"))
    if not png_files:
        print(f"❌ В папке '{input_folder.name}' нет PNG-файлов.")
        return

    combined_pdf = current_dir / "combined.pdf"

    print(f"\n✅ Найдено {len(png_files)} PNG-файлов в '{input_folder.name}'")
    print(f"Создаётся файл: {combined_pdf.name}")

    try:
        images = [Image.open(f).convert("RGB") for f in png_files]
        images[0].save(combined_pdf, save_all=True, append_images=images[1:])
        print("✅ Объединение завершено.")
    except Exception as e:
        print(f"❌ Ошибка при создании PDF: {e}")


def split_combined_pdf():
    current_dir = Path.cwd()
    combined_pdf = current_dir / "combined.pdf"

    if not combined_pdf.exists():
        print("❌ Файл combined.pdf не найден. Сначала используйте режим 2.")
        return

    try:
        n = int(input("На сколько частей разделить combined.pdf? Введите число (≥1): "))
        if n < 1:
            print("❌ Число должно быть ≥1.")
            return
    except ValueError:
        print("❌ Неверный ввод.")
        return

    reader = PdfReader(combined_pdf)
    total_pages = len(reader.pages)

    if n > total_pages:
        print(f"⚠️  Запрошено {n} частей, но в combined.pdf всего {total_pages} стр. Создадим {total_pages} файл(а) по 1 стр.")
        n = total_pages

    base_size = total_pages // n
    remainder = total_pages % n
    chunks = []
    start = 0
    for i in range(n):
        size = base_size + (1 if i < remainder else 0)
        end = start + size
        chunks.append((start, end))
        start = end

    split_dir = current_dir / "PDF_Split_Combined"
    split_dir.mkdir(exist_ok=True)

    for i, (start_page, end_page) in enumerate(chunks, 1):
        writer = PdfWriter()
        for p in range(start_page, end_page):
            writer.add_page(reader.pages[p])
        out_path = split_dir / f"combined_part_{i}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        print(f"   → {out_path.name}")

    print("✅ combined.pdf разделён.")


def resize_png_files():
    current_dir = Path.cwd()
    output_dir = current_dir / "PNG_Output"
    resized_dir = current_dir / "PNG_Resized"
    png_files = sorted(output_dir.glob("*.png"))

    if not png_files:
        print("❌ Нет PNG-файлов в PNG_Output.")
        return

    print("\n💡 Как масштабировать:")
    print("  • Введите число и 'x' на конце.")
    print("  • Примеры:")
    print("      2x   → увеличить в 2 раза")
    print("      0.5x → уменьшить в 2 раза")
    print("      1.4x → увеличить на 40%")
    print("      0.25x → уменьшить в 4 раза\n")

    user_input = input("Введите масштаб (например: 2x, 0.5x, 1.4x): ").strip().lower()

    if not user_input.endswith('x'):
        print("❌ Ошибка: введите значение в формате 'числоx' (например: 2x).")
        return

    try:
        factor_str = user_input[:-1]
        factor = float(factor_str)
        if factor <= 0:
            print("❌ Масштаб должен быть больше 0.")
            return
    except ValueError:
        print("❌ Неверное число. Пример: 0.5x, 2x, 1.25x")
        return

    resized_dir.mkdir(exist_ok=True)
    print(f"\n📏 Масштаб: {user_input} → коэффициент = {factor}")
    print(f"Исходные файлы: {output_dir}")
    print(f"Результат сохраняется в: {resized_dir}")
    print(f"Обработка {len(png_files)} файлов...")

    for png_path in png_files:
        try:
            with Image.open(png_path) as img:
                new_w = max(1, int(img.width * factor))
                new_h = max(1, int(img.height * factor))
                resized = img.resize((new_w, new_h), Image.LANCZOS)
                resized.save(resized_dir / png_path.name, "PNG")
                print(f"   → {png_path.name}: {img.width}×{img.height} → {new_w}×{new_h}")
        except Exception as e:
            print(f"❌ Ошибка при обработке {png_path.name}: {e}")
            continue

    print("✅ Масштабирование завершено. Файлы сохранены в PNG_Resized.")


def main():
    if 'путь' in POPPLER_PATH:
        print("🚨 ОШИБКА: Укажите правильный путь к Poppler.")
        return

    print("PDF ↔ PNG Toolkit by AlikAnimeha")
    print("GitHub: https://github.com/AlikAnimeha/PDF-PNG-Toolkit\n")

    print("Выберите режим:")
    print("1 — PDF из PDF_Files → PNG в PNG_Output")
    print("2 — Объединить PNG из выбранной папки в один PDF")
    print("3 — Разделить combined.pdf на N частей")
    print("4 — Масштабировать PNG из PNG_Output → PNG_Resized")
    choice = input("Введите 1, 2, 3 или 4: ").strip()

    if choice == "1":
        convert_pdfs_to_png(POPPLER_PATH)
    elif choice == "2":
        combine_png_to_pdf()
    elif choice == "3":
        split_combined_pdf()
    elif choice == "4":
        resize_png_files()
    else:
        print("❌ Неверный выбор.")
        return

    print("\n✨ Готово.")


if __name__ == "__main__":
    main()