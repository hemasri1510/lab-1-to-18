"""
Lab 3.2 - Migrate Referenced to Embedded Design

Demonstrates:
1. Referenced posts and comments
2. $lookup to join posts with comments
3. Migration to embedded comments
4. Query comparison between referenced and embedded designs
"""

import sys
import os
from datetime import datetime

# Allow importing config from Activity_3.1
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from config.connection import get_db, banner


# ============================================================
# SAMPLE POSTS
# ============================================================

POSTS = [
    {
        "post_id": 1,
        "title": "Beautiful Travel Destination",
        "author": "Arjun",
        "content": "Exploring beautiful places and enjoying nature.",
        "media": {
            "type": "image",
            "source": "Pinterest",
            "url": "https://in.pinterest.com/pin/1002473198305670082/"
        },
        "created_at": datetime(2026, 9, 1)
    },
    {
        "post_id": 2,
        "title": "My Tech Setup",
        "author": "Sneha",
        "content": "Sharing my simple and aesthetic study setup.",
        "media": {
            "type": "image",
            "source": "Pinterest",
            "url": "https://in.pinterest.com/pin/1105281933548985957/"
        },
        "created_at": datetime(2026, 9, 2)
    },
    {
        "post_id": 3,
        "title": "Food Photography",
        "author": "Rahul",
        "content": "Trying some food photography techniques today.",
        "media": {
            "type": "image",
            "source": "Pinterest",
            "url": "https://in.pinterest.com/pin/18999629672144745/"
        },
        "created_at": datetime(2026, 9, 3)
    },
    {
        "post_id": 4,
        "title": "Nature Photography",
        "author": "Divya",
        "content": "A peaceful day surrounded by nature.",
        "media": {
            "type": "image",
            "source": "Pinterest",
            "url": "https://in.pinterest.com/pin/aesthetic-photography-nature--777433954451544172/"
        },
        "created_at": datetime(2026, 9, 4)
    },
    {
        "post_id": 5,
        "title": "Travel Video",
        "author": "Vikram",
        "content": "Sharing an interesting travel video.",
        "media": {
            "type": "video",
            "source": "YouTube",
            "url": "https://www.youtube.com/watch?v=WA69w6hYTWs"
        },
        "created_at": datetime(2026, 9, 5)
    }
]


# ============================================================
# 10 COMMENTS
# ============================================================

COMMENTS = [
    {
        "comment_id": 1,
        "post_id": 1,
        "author": "Kavya",
        "text": "This place looks amazing!",
        "created_at": datetime(2026, 9, 1)
    },
    {
        "comment_id": 2,
        "post_id": 1,
        "author": "Neha",
        "text": "I would love to visit this place.",
        "created_at": datetime(2026, 9, 1)
    },
    {
        "comment_id": 3,
        "post_id": 2,
        "author": "Arjun",
        "text": "Your setup looks really clean.",
        "created_at": datetime(2026, 9, 2)
    },
    {
        "comment_id": 4,
        "post_id": 2,
        "author": "Vikram",
        "text": "The setup is simple and nice.",
        "created_at": datetime(2026, 9, 2)
    },
    {
        "comment_id": 5,
        "post_id": 3,
        "author": "Sneha",
        "text": "The food looks delicious!",
        "created_at": datetime(2026, 9, 3)
    },
    {
        "comment_id": 6,
        "post_id": 3,
        "author": "Divya",
        "text": "Great photography skills.",
        "created_at": datetime(2026, 9, 3)
    },
    {
        "comment_id": 7,
        "post_id": 4,
        "author": "Rahul",
        "text": "Nature always looks beautiful.",
        "created_at": datetime(2026, 9, 4)
    },
    {
        "comment_id": 8,
        "post_id": 4,
        "author": "Kavya",
        "text": "Such a peaceful view!",
        "created_at": datetime(2026, 9, 4)
    },
    {
        "comment_id": 9,
        "post_id": 5,
        "author": "Neha",
        "text": "Nice travel video.",
        "created_at": datetime(2026, 9, 5)
    },
    {
        "comment_id": 10,
        "post_id": 5,
        "author": "Arjun",
        "text": "This makes me want to travel.",
        "created_at": datetime(2026, 9, 5)
    }
]


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    banner("Lab 3.2: Referenced to Embedded Design")

    db = get_db("nosql_labs")

    # --------------------------------------------------------
    # 1. Create referenced collections
    # --------------------------------------------------------

    if "posts_referenced" in db.list_collection_names():
        db.drop_collection("posts_referenced")

    if "comments_referenced" in db.list_collection_names():
        db.drop_collection("comments_referenced")

    posts_ref = db["posts_referenced"]
    comments_ref = db["comments_referenced"]

    posts_ref.insert_many(POSTS)
    comments_ref.insert_many(COMMENTS)

    print("[OK] Created referenced collections.")
    print(f"[OK] Inserted {len(POSTS)} posts.")
    print(f"[OK] Inserted {len(COMMENTS)} comments.")

    # --------------------------------------------------------
    # 2. Display referenced comments
    # --------------------------------------------------------

    print("\n=== Referenced Comments ===")

    for comment in comments_ref.find({}, {"_id": 0}):
        print(
            f"  Comment {comment['comment_id']} "
            f"-> Post {comment['post_id']}: "
            f"{comment['text']}"
        )

    # --------------------------------------------------------
    # 3. Use $lookup
    # --------------------------------------------------------

    print("\n=== $lookup: Posts with Comments ===")

    pipeline = [
        {
            "$lookup": {
                "from": "comments_referenced",
                "localField": "post_id",
                "foreignField": "post_id",
                "as": "comments"
            }
        },
        {
            "$project": {
                "_id": 0,
                "post_id": 1,
                "title": 1,
                "comments.comment_id": 1,
                "comments.author": 1,
                "comments.text": 1
            }
        }
    ]

    joined_posts = posts_ref.aggregate(pipeline)

    for post in joined_posts:
        print(
            f"\n  Post {post['post_id']}: "
            f"{post['title']}"
        )

        for comment in post["comments"]:
            print(
                f"    - {comment['author']}: "
                f"{comment['text']}"
            )

    # --------------------------------------------------------
    # 4. Create embedded design
    # --------------------------------------------------------

    if "posts_embedded" in db.list_collection_names():
        db.drop_collection("posts_embedded")

    posts_embedded = db["posts_embedded"]

    embedded_documents = []

    for post in POSTS:

        post_copy = post.copy()

        post_comments = list(
            comments_ref.find(
                {"post_id": post["post_id"]},
                {"_id": 0, "post_id": 0}
            )
        )

        post_copy["comments"] = post_comments

        embedded_documents.append(post_copy)

    posts_embedded.insert_many(embedded_documents)

    print("\n[OK] Created 'posts_embedded' collection.")
    print("[OK] Migrated comments into posts.")

    # --------------------------------------------------------
    # 5. Display embedded documents
    # --------------------------------------------------------

    print("\n=== Embedded Posts ===")

    for post in posts_embedded.find({}, {"_id": 0}):

        print(
            f"\n  Post {post['post_id']}: "
            f"{post['title']}"
        )

        print(
            f"  Media: "
            f"{post['media']['type']} "
            f"({post['media']['source']})"
        )

        for comment in post["comments"]:
            print(
                f"    - {comment['author']}: "
                f"{comment['text']}"
            )

    # --------------------------------------------------------
    # 6. Compare queries
    # --------------------------------------------------------

    print("\n=== Query Comparison ===")

    print("\nReferenced Design:")
    referenced_result = list(
        posts_ref.aggregate([
            {
                "$match": {
                    "post_id": 1
                }
            },
            {
                "$lookup": {
                    "from": "comments_referenced",
                    "localField": "post_id",
                    "foreignField": "post_id",
                    "as": "comments"
                }
            }
        ])
    )

    if referenced_result:
        print(
            f"  Post 1 retrieved with "
            f"{len(referenced_result[0]['comments'])} comments."
        )

    print("\nEmbedded Design:")

    embedded_result = posts_embedded.find_one(
        {"post_id": 1},
        {"_id": 0, "comments": 1}
    )

    if embedded_result:
        print(
            f"  Post 1 retrieved with "
            f"{len(embedded_result['comments'])} comments."
        )

    # --------------------------------------------------------
    # 7. Design comparison
    # --------------------------------------------------------

    print("\n=== Design Comparison ===")

    print("Referenced Design:")
    print("  - Posts and comments are stored separately.")
    print("  - Requires $lookup to retrieve related comments.")
    print("  - Useful when comments are very large or independent.")

    print("\nEmbedded Design:")
    print("  - Comments are stored inside each post.")
    print("  - Related comments can be retrieved with the post.")
    print("  - Useful when comments are limited and usually accessed with the post.")

    print("\n=== Migration Complete ===")
    print("[OK] 5 posts migrated.")
    print("[OK] 10 comments embedded.")


if __name__ == "__main__":
    main()