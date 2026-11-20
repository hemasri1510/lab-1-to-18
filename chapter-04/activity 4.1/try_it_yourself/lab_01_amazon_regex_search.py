"""
Lab 4.1 - Try It Yourself
Regex Product Name Search

Searches Amazon category/product names using
MongoDB $regex operator with case-insensitive matching.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, banner


def regex_search_products(col, search_string):
    """
    Search product names using case-insensitive regex.
    """

    query = {
        "name": {
            "$regex": search_string,
            "$options": "i"
        }
    }

    results = list(
        col.find(
            query,
            {
                "_id": 0,
                "sku": 1,
                "name": 1,
                "amazon_id": 1,
                "category": 1,
                "price": 1,
                "stock": 1,
                "tags": 1
            }
        ).sort("name", 1)
    )

    return results


def main():

    banner("Lab 4.1: Try It Yourself - Regex Search")

    # --------------------------------------------------
    # Connect to existing Amazon collection
    # --------------------------------------------------

    db = get_db("nosql_labs")

    col = db["amazon_products"]

    # --------------------------------------------------
    # Search string
    # --------------------------------------------------

    search_string = "sewing"

    print(
        f"=== Regex Search: '{search_string}' "
        f"(case-insensitive) ===\n"
    )

    results = regex_search_products(
        col,
        search_string
    )

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    if results:

        for r in results:

            print(
                f"  {r['name']:<45} "
                f"Amazon ID={r['amazon_id']}"
            )

        print(
            f"\n[OK] Found {len(results)} matching products."
        )

    else:

        print("[INFO] No matching products found.")

    # --------------------------------------------------
    # Export matching results to JSON
    # --------------------------------------------------

    json_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "amazon_regex_results.json"
    )

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"[OK] Regex results exported to: {json_file}"
    )

    # --------------------------------------------------
    # Complete
    # --------------------------------------------------

    banner("Try It Yourself Complete")


if __name__ == "__main__":
    main()