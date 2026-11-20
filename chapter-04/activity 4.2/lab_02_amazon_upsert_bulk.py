"""
Lab 4.2 - Upsert and Bulk Operations
Amazon Dataset Version

Demonstrates:
1. Upsert with an existing SKU
2. Upsert with a new SKU
3. Bulk write using UpdateOne
4. $inc operation
5. $mul operation
6. $set operation
7. Bulk upsert
8. Idempotency demonstration
"""

import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from config.connection import get_db, banner
from pymongo import UpdateOne


def show_product(col, sku):
    """Display one product."""

    product = col.find_one(
        {"sku": sku},
        {"_id": 0}
    )

    if product:
        print(
            f"  {product['sku']} | "
            f"{product['name']} | "
            f"price=${product.get('price', 0):.2f} | "
            f"stock={product.get('stock', 0)} | "
            f"active={product.get('active', True)}"
        )
    else:
        print(f"  {sku} not found.")


def main():

    banner("Lab 4.2: Amazon Upsert and Bulk Operations")

    # ========================================================
    # CONNECT TO DATABASE
    # ========================================================

    db = get_db("nosql_labs")

    col = db["amazon_products"]

    print(
        f"[OK] Connected to amazon_products collection."
    )

    print(
        f"[OK] Current documents: "
        f"{col.count_documents({})}"
    )

    # ========================================================
    # 1. UPSERT - EXISTING SKU
    # ========================================================

    print(
        "\n=== 1. Upsert: Existing SKU ==="
    )

    existing_sku = "AMZ-001"

    result = col.update_one(
        {"sku": existing_sku},
        {
            "$set": {
                "price": 279.99,
                "stock": 45
            }
        },
        upsert=True
    )

    if result.matched_count > 0:

        print(
            f"[OK] {existing_sku} already exists "
            f"- product updated."
        )

        print(
            f"    Modified count: "
            f"{result.modified_count}"
        )

    elif result.upserted_id is not None:

        print(
            f"[OK] {existing_sku} did not exist "
            f"- product inserted."
        )

        print(
            f"    Upserted ID: "
            f"{result.upserted_id}"
        )

    show_product(col, existing_sku)

    # ========================================================
    # 2. UPSERT - NEW SKU
    # ========================================================

    print(
        "\n=== 2. Upsert: New SKU ==="
    )

    new_sku = "AMZ-NEW-001"

    result = col.update_one(
        {"sku": new_sku},
        {
            "$set": {
                "name": "Amazon New Product",
                "category": "Amazon Category",
                "amazon_id": 9999,
                "price": 199.99,
                "stock": 100,
                "tags": [
                    "electronics",
                    "wireless"
                ],
                "active": True
            }
        },
        upsert=True
    )

    if result.upserted_id is not None:

        print(
            f"[OK] {new_sku} did not exist "
            f"- new product inserted."
        )

        print(
            f"    Upserted ID: "
            f"{result.upserted_id}"
        )

    else:

        print(
            f"[OK] {new_sku} already existed "
            f"- product updated."
        )

        print(
            f"    Modified count: "
            f"{result.modified_count}"
        )

    show_product(col, new_sku)

    # ========================================================
    # 3. BULK WRITE
    # ========================================================

    print(
        "\n=== 3. Bulk Write Operations ==="
    )

    operations = [

        # ----------------------------------------------------
        # Operation 1: Increase stock by 10
        # ----------------------------------------------------

        UpdateOne(
            {"sku": "AMZ-001"},
            {
                "$inc": {
                    "stock": 10
                }
            }
        ),

        # ----------------------------------------------------
        # Operation 2: Increase stock by 10
        # ----------------------------------------------------

        UpdateOne(
            {"sku": "AMZ-002"},
            {
                "$inc": {
                    "stock": 10
                }
            }
        ),

        # ----------------------------------------------------
        # Operation 3: Reduce price by 10%
        # ----------------------------------------------------

        UpdateOne(
            {"sku": "AMZ-003"},
            {
                "$mul": {
                    "price": 0.90
                }
            }
        ),

        # ----------------------------------------------------
        # Operation 4: Set product active
        # ----------------------------------------------------

        UpdateOne(
            {"sku": "AMZ-004"},
            {
                "$set": {
                    "active": True
                }
            }
        ),

        # ----------------------------------------------------
        # Operation 5: Upsert a new product
        # ----------------------------------------------------

        UpdateOne(
            {"sku": "AMZ-BULK-001"},
            {
                "$set": {
                    "name": "Bulk Insert Amazon Product",
                    "category": "Amazon Category",
                    "amazon_id": 10000,
                    "price": 149.99,
                    "stock": 50,
                    "tags": [
                        "general",
                        "popular"
                    ],
                    "active": True
                }
            },
            upsert=True
        )
    ]

    result = col.bulk_write(
        operations,
        ordered=True
    )

    print(
        f"[OK] Bulk write completed."
    )

    print(
        f"    Matched: {result.matched_count}"
    )

    print(
        f"    Modified: {result.modified_count}"
    )

    print(
        f"    Upserted: {len(result.upserted_ids)}"
    )

    if result.upserted_ids:

        print(
            f"    Upserted IDs: "
            f"{result.upserted_ids}"
        )

    # ========================================================
    # 4. VERIFY BULK OPERATIONS
    # ========================================================

    print(
        "\n=== 4. Verify Bulk Operations ==="
    )

    print("\nAMZ-001:")

    show_product(
        col,
        "AMZ-001"
    )

    print("\nAMZ-002:")

    show_product(
        col,
        "AMZ-002"
    )

    print("\nAMZ-003:")

    show_product(
        col,
        "AMZ-003"
    )

    print("\nAMZ-004:")

    show_product(
        col,
        "AMZ-004"
    )

    print("\nAMZ-BULK-001:")

    show_product(
        col,
        "AMZ-BULK-001"
    )

    # ========================================================
    # 5. RUN THE SAME BULK OPERATIONS AGAIN
    # ========================================================

    print(
        "\n=== 5. Idempotency Test ==="
    )

    print(
        "Running the same bulk operations again..."
    )

    result2 = col.bulk_write(
        operations,
        ordered=True
    )

    print(
        f"[OK] Second bulk write completed."
    )

    print(
        f"    Matched: {result2.matched_count}"
    )

    print(
        f"    Modified: {result2.modified_count}"
    )

    print(
        f"    Upserted: {len(result2.upserted_ids)}"
    )

    # ========================================================
    # 6. VERIFY IDEMPOTENCY
    # ========================================================

    print(
        "\n=== 6. Idempotency Results ==="
    )

    print(
        "\nAMZ-001 after second run:"
    )

    show_product(
        col,
        "AMZ-001"
    )

    print(
        "\nAMZ-003 after second run:"
    )

    show_product(
        col,
        "AMZ-003"
    )

    print(
        "\nAMZ-004 after second run:"
    )

    show_product(
        col,
        "AMZ-004"
    )

    print(
        "\nAMZ-BULK-001 after second run:"
    )

    show_product(
        col,
        "AMZ-BULK-001"
    )

    # ========================================================
    # 7. EXPLANATION
    # ========================================================

    print(
        "\n=== 7. Operation Behavior ==="
    )

    print(
        "  $set : Idempotent - repeated execution "
        "keeps the same value."
    )

    print(
        "  $inc : Non-idempotent - repeated execution "
        "changes the value again."
    )

    print(
        "  $mul : Non-idempotent - repeated execution "
        "multiplies the value again."
    )

    print(
        "  Upsert: Existing SKU is updated; "
        "missing SKU is inserted."
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    banner(
        "Lab 4.2 Amazon Upsert and Bulk Operations Complete"
    )


if __name__ == "__main__":
    main()