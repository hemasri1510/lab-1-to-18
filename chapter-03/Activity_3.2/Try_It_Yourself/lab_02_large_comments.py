"""
Lab 3.2 - Try It Yourself

Question:
If a post has 10,000 comments, should all comments be embedded?

Decision:
No. For very large comment arrays, a referenced design is more suitable.
"""

import sys
import os

# Allow importing config from Activity_3.2
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from config.connection import get_db, banner


def main():

    banner("Lab 3.2 - Try It Yourself: Large Comments")

    db = get_db("nosql_labs")

    # Create separate comments collection
    if "large_comments_referenced" in db.list_collection_names():
        db.drop_collection("large_comments_referenced")

    comments = db["large_comments_referenced"]

    # Simulate 10,000 comments
    large_comments = []

    for i in range(1, 10001):
        large_comments.append({
            "comment_id": i,
            "post_id": 1,
            "author": f"User{i}",
            "text": f"Comment number {i}"
        })

    comments.insert_many(large_comments)

    print("[OK] Created large_comments_referenced collection.")
    print("[OK] Inserted 10,000 comments for Post 1.")

    # Show a few comments
    print("\n=== Sample Comments ===")

    for comment in comments.find(
        {"post_id": 1},
        {"_id": 0}
    ).limit(3):
        print(
            f"  Comment {comment['comment_id']}: "
            f"{comment['text']}"
        )

    print("\n=== Design Decision ===")

    print(
        "Embedding 10,000 comments inside one post is not recommended."
    )

    print(
        "A very large embedded array can make the post document large "
        "and make updates and retrieval less efficient."
    )

    print(
        "For this case, comments should be stored in a separate "
        "collection and linked using post_id."
    )

    print(
        "Pagination can be used to retrieve comments in smaller batches."
    )

    print("\n=== Recommended Design ===")
    print("  posts collection")
    print("       |")
    print("       | post_id")
    print("       v")
    print("  comments collection")
    print("       |")
    print("       +-- Comment 1")
    print("       +-- Comment 2")
    print("       +-- ...")
    print("       +-- Comment 10,000")

    banner("Try It Yourself Complete")


if __name__ == "__main__":
    main()