"""Lab 3.1 - Try It Yourself
Add prerequisite relationships between courses.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, banner


COURSES = [
    {
        "course_name": "Introduction to Machine Learning",
        "course_code": "AIML101",
        "instructor": "Dr. Priya Sharma",
        "credits": 4,
        "prerequisites": [],
        "schedule": {
            "days": ["Monday", "Wednesday"],
            "time": "10:00-11:30",
            "room": "LH-201"
        },
        "enrolled_students": [
            {
                "name": "Arjun Mehta",
                "email": "arjun@college.edu",
                "grade": "A"
            },
            {
                "name": "Sneha Reddy",
                "email": "sneha@college.edu",
                "grade": "B+"
            },
            {
                "name": "Rahul Kumar",
                "email": "rahul@college.edu",
                "grade": "A-"
            },
            {
                "name": "Divya Patel",
                "email": "divya@college.edu",
                "grade": "B"
            },
        ]
    },
    {
        "course_name": "Deep Learning with PyTorch",
        "course_code": "AIML301",
        "instructor": "Dr. Anil Gupta",
        "credits": 3,
        "prerequisites": ["AIML101"],
        "schedule": {
            "days": ["Tuesday", "Thursday"],
            "time": "14:00-15:30",
            "room": "LH-305"
        },
        "enrolled_students": [
            {
                "name": "Arjun Mehta",
                "email": "arjun@college.edu",
                "grade": None
            },
            {
                "name": "Kavya Nair",
                "email": "kavya@college.edu",
                "grade": "A"
            },
            {
                "name": "Vikram Singh",
                "email": "vikram@college.edu",
                "grade": "A+"
            },
        ]
    },
    {
        "course_name": "Natural Language Processing",
        "course_code": "AIML201",
        "instructor": "Dr. Meera Joshi",
        "credits": 3,
        "prerequisites": ["AIML101"],
        "schedule": {
            "days": ["Monday", "Wednesday", "Friday"],
            "time": "09:00-10:00",
            "room": "LH-102"
        },
        "enrolled_students": [
            {
                "name": "Sneha Reddy",
                "email": "sneha@college.edu",
                "grade": "B+"
            },
            {
                "name": "Rahul Kumar",
                "email": "rahul@college.edu",
                "grade": None
            },
            {
                "name": "Priya Das",
                "email": "priya.d@college.edu",
                "grade": "A-"
            },
            {
                "name": "Arjun Mehta",
                "email": "arjun@college.edu",
                "grade": None
            },
            {
                "name": "Neha Gupta",
                "email": "neha@college.edu",
                "grade": "B"
            },
        ]
    },
]


# JSON Schema for validation
COURSE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "course_name",
            "course_code",
            "instructor",
            "prerequisites",
            "schedule",
            "enrolled_students"
        ],
        "properties": {
            "course_name": {
                "bsonType": "string",
                "description": "Course name is required"
            },
            "course_code": {
                "bsonType": "string",
                "pattern": r"^[A-Z]{4}\d{3}$",
                "description": "Format: XXXX000"
            },
            "instructor": {
                "bsonType": "string",
                "description": "Instructor name is required"
            },
            "credits": {
                "bsonType": "int",
                "minimum": 1,
                "maximum": 6
            },
            "prerequisites": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string"
                },
                "description": "List of prerequisite course codes"
            },
            "schedule": {
                "bsonType": "object",
                "required": ["days", "time", "room"],
                "properties": {
                    "days": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "time": {
                        "bsonType": "string"
                    },
                    "room": {
                        "bsonType": "string"
                    },
                }
            },
            "enrolled_students": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {
                            "bsonType": "string"
                        },
                        "email": {
                            "bsonType": "string"
                        },
                        "grade": {
                            "bsonType": ["string", "null"]
                        },
                    }
                }
            },
        }
    }
}


def main():
    banner("Lab 3.1 - Try It Yourself: Course Prerequisites")

    db = get_db("nosql_labs")

    # Drop and recreate collection with validation
    if "courses_prerequisites" in db.list_collection_names():
        db.drop_collection("courses_prerequisites")

    db.create_collection(
        "courses_prerequisites",
        validator=COURSE_VALIDATOR
    )

    col = db["courses_prerequisites"]

    print("[OK] Created 'courses_prerequisites' collection.")
    print("[OK] JSON Schema validation includes prerequisites.\n")

    # Insert courses
    col.insert_many(COURSES)

    print(f"[OK] Inserted {len(COURSES)} courses.\n")

    # Display prerequisite relationships
    print("=== Course Prerequisites ===")

    for course in col.find(
        {},
        {
            "course_name": 1,
            "course_code": 1,
            "prerequisites": 1,
            "_id": 0
        }
    ):
        prerequisites = course["prerequisites"]

        if prerequisites:
            print(
                f"  {course['course_code']} - "
                f"{course['course_name']}: "
                f"{', '.join(prerequisites)}"
            )
        else:
            print(
                f"  {course['course_code']} - "
                f"{course['course_name']}: None"
            )

    # Find courses that require AIML101
    print("\n=== Courses Requiring AIML101 ===")

    dependent_courses = col.find(
        {"prerequisites": "AIML101"},
        {
            "course_name": 1,
            "course_code": 1,
            "_id": 0
        }
    )

    for course in dependent_courses:
        print(
            f"  {course['course_code']}: "
            f"{course['course_name']}"
        )

    # Explain the design decision
    print("\n=== Design Decision ===")
    print(
        "Prerequisites are referenced using course codes "
        "instead of embedding complete course documents."
    )
    print(
        "This avoids duplicating course information and keeps "
        "the prerequisite relationship simple to maintain."
    )

    banner("Try It Yourself Complete")


if __name__ == "__main__":
    main()