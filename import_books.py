"""
Script to import books from CSV into database
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def main():
    """Import books from CSV"""
    try:
        from caelio_care.database import init_database, import_books_from_csv
        
        print("🔌 Connecting to database...")
        await init_database()
        
        print("\n📚 Importing books from CSV...")
        success = await import_books_from_csv()
        
        if success:
            print("\n✅ Books imported successfully!")
        else:
            print("\n❌ Failed to import books")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
