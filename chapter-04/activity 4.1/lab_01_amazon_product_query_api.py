"""
Lab 4.1 - Build a Product Query API
Amazon Categories Dataset Version

Required concepts:
- Schema validation
- Comparison operators
- Logical operators
- Array operators
- Projection
- Pagination
- Regex search
"""

import sys
import os
import csv
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner


# ============================================================
# LOAD AMAZON DATASET
# ============================================================

def load_amazon_dataset(csv_file):
    """
    Load Amazon category dataset.

    Original Amazon dataset contains:
        id
        category_name

    Additional fields required by Lab 4.1
    are derived from the dataset so that
    all required MongoDB operators can be demonstrated.
    """

    products = []

    with open(csv_file, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            amazon_id = int(row["id"])
            category = row["category_name"].strip()

            # ------------------------------------------------
            # Derived fields for the lab
            # ------------------------------------------------

            # Generate a deterministic price between 20 and 150
            price = 20 + ((amazon_id * 17) % 131)

            # Generate stock values
            stock = (amazon_id * 7) % 51

            # Create tags based on the category name
            tags = []

            category_lower = category.lower()

            if any(word in category_lower
                   for word in ["electronics", "automotive", "computer"]):
                tags.append("electronics")

            if any(word in category_lower
                   for word in ["wireless", "bluetooth"]):
                tags.append("wireless")

            if any(word in category_lower
                   for word in ["craft", "sewing", "art", "painting",
                                "knitting", "scrapbooking", "needlework"]):
                tags.append("crafts")

            if "home" in category_lower:
                tags.append("home")

            # Make sure every product has at least one tag
            if not tags:
                tags.append("general")

            # Add a second tag for some records
            if amazon_id % 3 == 0 and len(tags) < 2:
                tags.append("popular")

            product = {
                "sku": f"AMZ-{amazon_id:03d}",
                "name": category,
                "amazon_id": amazon_id,
                "category": category,
                "price": float(price),
                "stock": int(stock),
                "tags": tags
            }

            products.append(product)

    return products


# ============================================================
# PAGINATION FUNCTION
# ============================================================

def search_products(
    col,
    query_filter,
    projection=None,
    page=1,
    page_size=5
):
    """
    Return one page of products sorted by name.
    """

    skip = (page - 1) * page_size

    cursor = col.find(
        query_filter,
        projection
    ).sort("name", 1)

    total = col.count_documents(query_filter)

    results = list(
        cursor.skip(skip).limit(page_size)
    )

    return results, total


# ============================================================
# MAIN
# ============================================================

def main():

    banner("Lab 4.1: Amazon Product Query API")

    # ========================================================
    # CONNECT TO DATABASE
    # ========================================================

    db = get_db("nosql_labs")

    col = reset_collection(
        "nosql_labs",
        "amazon_products"
    )

    # ========================================================
    # LOAD CSV
    # ========================================================

    csv_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "amazon_categories.csv"
    )

    products = load_amazon_dataset(csv_file)

    # ========================================================
    # INSERT DATA
    # ========================================================

    col.insert_many(products)

    print(
        f"[OK] Inserted {len(products)} Amazon category products.\n"
    )

    # ========================================================
    # 1. COMPARISON OPERATORS
    # ========================================================

    print(
        "=== 1. Comparison: Price between 20 and 50 ==="
    )

    results = col.find(
        {
            "price": {
                "$gte": 20,
                "$lte": 50
            }
        },
        {
            "name": 1,
            "price": 1,
            "_id": 0
        }
    ).limit(10)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"price=${r['price']:.2f}"
        )

    # --------------------------------------------------------
    # Stock equal to zero
    # --------------------------------------------------------

    print(
        "\n=== 1B. Comparison: Products with stock = 0 ==="
    )

    results = col.find(
        {
            "stock": {
                "$eq": 0
            }
        },
        {
            "name": 1,
            "stock": 1,
            "_id": 0
        }
    ).limit(10)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"stock={r['stock']}"
        )

    # ========================================================
    # 2. LOGICAL OPERATORS
    # ========================================================

    print(
        "\n=== 2. Logical: Out of stock OR price above 100 ==="
    )

    results = col.find(
        {
            "$or": [
                {
                    "stock": 0
                },
                {
                    "price": {
                        "$gt": 100
                    }
                }
            ]
        },
        {
            "name": 1,
            "price": 1,
            "stock": 1,
            "_id": 0
        }
    ).limit(15)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"price=${r['price']:.2f} "
            f"stock={r['stock']}"
        )

    # --------------------------------------------------------
    # AND condition
    # --------------------------------------------------------

    print(
        "\n=== 2B. Logical: In stock AND tagged 'premium' ==="
    )

    # Add a premium tag to selected records for demonstration
    col.update_many(
        {
            "price": {
                "$gt": 100
            }
        },
        {
            "$addToSet": {
                "tags": "premium"
            }
        }
    )

    results = col.find(
        {
            "$and": [
                {
                    "stock": {
                        "$gt": 0
                    }
                },
                {
                    "tags": "premium"
                }
            ]
        },
        {
            "name": 1,
            "stock": 1,
            "tags": 1,
            "_id": 0
        }
    ).limit(10)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"stock={r['stock']} "
            f"tags={r['tags']}"
        )

    # ========================================================
    # 3. ARRAY OPERATORS
    # ========================================================

    print(
        "\n=== 3. Array: Products having BOTH "
        "'electronics' AND 'wireless' ==="
    )

    # Add both tags to some products for demonstration
    col.update_many(
        {
            "amazon_id": {
                "$in": [20, 40, 60, 80]
            }
        },
        {
            "$addToSet": {
                "tags": {
                    "$each": [
                        "electronics",
                        "wireless"
                    ]
                }
            }
        }
    )

    results = col.find(
        {
            "tags": {
                "$all": [
                    "electronics",
                    "wireless"
                ]
            }
        },
        {
            "name": 1,
            "tags": 1,
            "_id": 0
        }
    )

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"{r['tags']}"
        )

    # --------------------------------------------------------
    # Exactly 2 tags
    # --------------------------------------------------------

    print(
        "\n=== 3B. Array: Products with exactly 2 tags ==="
    )

    results = col.find(
        {
            "tags": {
                "$size": 2
            }
        },
        {
            "name": 1,
            "tags": 1,
            "_id": 0
        }
    ).limit(10)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"{r['tags']}"
        )

    # ========================================================
    # 4. PROJECTION
    # ========================================================

    print(
        "\n=== 4. Projection: Name and Amazon ID only ==="
    )

    results = col.find(
        {},
        {
            "name": 1,
            "amazon_id": 1,
            "_id": 0
        }
    ).sort("name", 1).limit(10)

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"Amazon ID={r['amazon_id']}"
        )

    # ========================================================
    # 5. PAGINATION
    # ========================================================

    print(
        "\n=== 5. Pagination: Page 1, size=5 ==="
    )

    page_results, total = search_products(
        col,
        {},
        {
            "name": 1,
            "price": 1,
            "_id": 0
        },
        page=1,
        page_size=5
    )

    for r in page_results:

        print(
            f"  {r['name']:<45} "
            f"${r['price']:.2f}"
        )

    print(
        f"  Showing {len(page_results)} "
        f"of {total} products"
    )

    # --------------------------------------------------------
    # PAGE 2
    # --------------------------------------------------------

    print(
        "\n=== 5B. Pagination: Page 2, size=5 ==="
    )

    page_results, _ = search_products(
        col,
        {},
        {
            "name": 1,
            "price": 1,
            "_id": 0
        },
        page=2,
        page_size=5
    )

    for r in page_results:

        print(
            f"  {r['name']:<45} "
            f"${r['price']:.2f}"
        )

    # ========================================================
    # 6. TRY IT YOURSELF - REGEX
    # ========================================================

    print(
        "\n=== 6. Try It Yourself: Regex search "
        "for 'sewing' ==="
    )

    results = col.find(
        {
            "name": {
                "$regex": "sewing",
                "$options": "i"
            }
        },
        {
            "name": 1,
            "amazon_id": 1,
            "_id": 0
        }
    )

    for r in results:

        print(
            f"  {r['name']:<45} "
            f"Amazon ID={r['amazon_id']}"
        )

    # ========================================================
    # EXPORT MONGODB JSON
    # ========================================================

    print(
        "\n=== Exporting MongoDB JSON ==="
    )

    all_products = list(
        col.find(
            {},
            {
                "_id": 0
            }
        )
    )

    json_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "amazon_products.json"
    )

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_products,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[OK] MongoDB JSON exported to: {json_file}"
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    banner("Lab 4.1 Amazon Dataset Complete")


if __name__ == "__main__":
    main()