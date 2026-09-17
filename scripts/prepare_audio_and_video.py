import json
import csv
import re
from pathlib import Path

# =========================
# CONFIGURAÇÃO
# =========================

INPUT_FILE = Path("data/raw/audio_and_video.ibyte.json")

OUTPUT_DIR = Path("data/processed")
OUTPUT_JSONL = OUTPUT_DIR / "audio_and_video_clean.jsonl"
OUTPUT_CSV = OUTPUT_DIR / "audio_and_video_clean.csv"


def clean_text(value):
    """
    Remove quebras de linha, tabs e espaços duplicados.
    """
    if not value:
        return ""

    value = str(value)
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def get_brand(product):
    """
    Extrai a marca.
    Exemplo no dataset:
    {"@type": "brand", "name": "JBL"}
    """
    brand = product.get("brand", "")

    if isinstance(brand, dict):
        return clean_text(brand.get("name", ""))

    return clean_text(brand)


def get_price(product):
    """
    Extrai o preço de:
    offers -> price
    """
    offers = product.get("offers", {})

    if isinstance(offers, dict):
        price = offers.get("price")

        if price is not None:
            try:
                return float(price)
            except (ValueError, TypeError):
                return price

    return None


def extract_products(data):
    """
    Percorre os registros procurando objetos
    do schema.org cujo @type seja Product.
    """
    products = []

    for record in data:
        if not isinstance(record, dict):
            continue

        microdata = record.get("microdata", [])

        if not isinstance(microdata, list):
            continue

        for item in microdata:
            if not isinstance(item, dict):
                continue

            if item.get("@type") != "Product":
                continue

            product = {
                "name": clean_text(item.get("name", "")),
                "description": clean_text(item.get("description", "")),
                "brand": get_brand(item),
                "sku": clean_text(item.get("sku", "")),
                "price": get_price(item),
            }

            if product["name"]:
                products.append(product)

    return products


def remove_duplicates(products):
    """
    Remove duplicados usando SKU como chave.
    Caso não exista SKU, utiliza o nome.
    """
    unique = {}

    for product in products:
        key = product["sku"] or product["name"].lower()

        if key not in unique:
            unique[key] = product

    return list(unique.values())


def save_jsonl(products):
    """
    Salva um produto por linha em JSONL.
    """
    with OUTPUT_JSONL.open("w", encoding="utf-8") as file:
        for product in products:
            json.dump(product, file, ensure_ascii=False)
            file.write("\n")


def save_csv(products):
    """
    Salva também em CSV para inspeção em Excel/Google Sheets.
    """
    fields = [
        "name",
        "description",
        "brand",
        "sku",
        "price",
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(products)


def main():
    if not INPUT_FILE.exists():
        print(f"ERRO: arquivo não encontrado: {INPUT_FILE}")
        print("Confirme se o arquivo está dentro de data/raw/")
        return

    print(f"Lendo: {INPUT_FILE}")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    products = extract_products(data)

    print(f"Produtos encontrados: {len(products)}")

    products = remove_duplicates(products)

    print(f"Produtos após remoção de duplicados: {len(products)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_jsonl(products)
    save_csv(products)

    print("\nArquivos criados:")
    print(f"JSONL: {OUTPUT_JSONL}")
    print(f"CSV:   {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
