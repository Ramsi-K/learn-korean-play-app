#!/usr/bin/env python3
"""
Simple script to clear the database by deleting the SQLite file
"""
import os
import sys

db_path = "data/hagxwon.db"

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Successfully deleted {db_path}")
    except Exception as e:
        print(f"Error deleting {db_path}: {e}")
        sys.exit(1)
else:
    print(f"Database file {db_path} does not exist")

print("Database cleared. Restart the server to reseed.")
