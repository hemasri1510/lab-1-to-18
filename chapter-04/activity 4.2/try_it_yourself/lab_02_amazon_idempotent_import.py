"""
Lab 4.2 - Try It Yourself
Idempotent Bulk Import

Imports Amazon category records using upsert logic.
The function can be run multiple times without
creating duplicate documents.
"""

import sys
import os
import csv
import json

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)

from config.connection import get_db, banner
from pymongo import UpdateOne


# ============================================================
# LOAD AMAZON DATA
# ============================================================

def load_amazon_categories(csv_file, limit=5):

    categories = []

    with open(
        csv_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            amazon_id = int(row["id"])
            category_name = row["category_name"].strip()

            product = {
                "sku": f"AMZ-ID-{amazon_id:03d}",
                "amazon_id": amazon_id,
                "name": category_name,
                "category": category_name,
                "price": float(
                    20 + ((amazon_id * 17) % 131)
                ),
                "stock": int(
                    (amazon_id * 7) % 51
                ),
                "tags": ["general"],
                "active": True
            }

            categories.append(product)

            if len(categories) == limit:
                break

    return categories


# ============================================================
# IDEMPOTENT BULK IMPORT
# ============================================================

def idempotent_bulk_import(col, products):

    operations = []

    for product in products:

        operations.append(
            UpdateOne(
                {
                    "sku": product["sku"]
                },
                {
                    "$set": product
                },
                upsert=True
            )
        )

    if not operations:
        return None

    result = col.bulk_write(
        operations,
        ordered=False
    )

    return result


# ============================================================
# EXPORT IMPORTED DOCUMENTS TO JSON
# ============================================================

def export_json(col, products, json_file):

    skus = [
        product["sku"]
        for product in products
    ]

    documents = list(
        col.find(
            {
                "sku": {
                    "$in": skus
                }
            },
            {
                "_id": 0
            }
        ).sort("sku", 1)
    )

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            indent=4,
            ensure_ascii=False
        )

    return documents


# ============================================================
# MAIN
# ============================================================

def main():

    banner(
        "Lab 4.2: Try It Yourself - "
        "Idempotent Bulk Import"
    )

    # --------------------------------------------------------
    # Connect to existing Amazon collection
    # --------------------------------------------------------

    db = get_db("nosql_labs")

    col = db["amazon_products"]

    print(
        f"[OK] Connected to amazon_products collection."
    )

    # --------------------------------------------------------
    # CSV location
    # --------------------------------------------------------

    csv_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        ),
        "amazon_categories.csv"
    )

    # --------------------------------------------------------
    # Load five Amazon records
    # --------------------------------------------------------

    products = load_amazon_categories(
        csv_file,
        limit=5
    )

    print(
        f"[OK] Loaded {len(products)} records from CSV."
    )

    print("\nRecords selected for import:")

    for product in products:

        print(
            f"  {product['sku']} | "
            f"{product['name']}"
        )

    # --------------------------------------------------------
    # Count before first import
    # --------------------------------------------------------

    before_count = col.count_documents({})

    print(
        f"\nDocuments before first import: "
        f"{before_count}"
    )

    # --------------------------------------------------------
    # FIRST IMPORT
    # --------------------------------------------------------

    print(
        "\n=== First Idempotent Bulk Import ==="
    )

    result1 = idempotent_bulk_import(
        col,
        products
    )

    print(
        f"[OK] First import completed."
    )

    print(
        f"  Matched: {result1.matched_count}"
    )

    print(
        f"  Modified: {result1.modified_count}"
    )

    print(
        f"  Upserted: {len(result1.upserted_ids)}"
    )

    # --------------------------------------------------------
    # Count after first import
    # --------------------------------------------------------

    after_first_count = col.count_documents({})

    print(
        f"Documents after first import: "
        f"{after_first_count}"
    )

    # --------------------------------------------------------
    # SECOND IMPORT
    # --------------------------------------------------------

    print(
        "\n=== Second Idempotent Bulk Import ==="
    )

    result2 = idempotent_bulk_import(
        col,
        products
    )

    print(
        f"[OK] Second import completed."
    )

    print(
        f"  Matched: {result2.matched_count}"
    )

    print(
        f"  Modified: {result2.modified_count}"
    )

    print(
        f"  Upserted: {len(result2.upserted_ids)}"
    )

    # --------------------------------------------------------
    # Count after second import
    # --------------------------------------------------------

    after_second_count = col.count_documents({})

    print(
        f"Documents after second import: "
        f"{after_second_count}"
    )

    # --------------------------------------------------------
    # VERIFY NO DUPLICATES
    # --------------------------------------------------------

    print(
        "\n=== Idempotency Verification ==="
    )

    imported_skus = [
        product["sku"]
        for product in products
    ]

    duplicate_count = (
        col.count_documents(
            {
                "sku": {
                    "$in": imported_skus
                }
            }
        )
    )

    expected_count = len(products)

    print(
        f"Expected imported documents: "
        f"{expected_count}"
    )

    print(
        f"Actual imported documents: "
        f"{duplicate_count}"
    )

    if duplicate_count == expected_count:

        print(
            "[OK] No duplicates created."
        )

        print(
            "[OK] Bulk import is idempotent."
        )

    else:

        print(
            "[ERROR] Duplicate documents detected."
        )

    # --------------------------------------------------------
    # Export JSON
    # --------------------------------------------------------

    json_file = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "amazon_idempotent_import.json"
    )

    export_json(
        col,
        products,
        json_file
    )

    print(
        f"\n[OK] MongoDB JSON exported to:"
    )

    print(
        f"  {json_file}"
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    banner(
        "Try It Yourself - "
        "Idempotent Bulk Import Complete"
    )


if __name__ == "__main__":
    main()