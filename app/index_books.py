from pathlib import Path
import fitz

from config import BOOKS_DIR

def read_pdf(pdf_path: Path):
    """Read text from one PDF."""
    text = ""

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()

    return text


def main():

    print("=" * 60)
    print("Akanksh 1.0 - Book Scanner")
    print("=" * 60)

    for subject in BOOKS_DIR.iterdir():

        if not subject.is_dir():
            continue

        print(f"\nSubject : {subject.name}")

        for pdf in sorted(subject.glob("*.pdf")):

            if pdf.name.lower() == "contents.pdf":
                continue

            print(f"Reading : {pdf.name}")

            text = read_pdf(pdf)

            print(f"Characters : {len(text)}")


if __name__ == "__main__":
    main()