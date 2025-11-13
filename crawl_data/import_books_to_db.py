"""
Script to import books from CSV into database
Usage: python import_books_to_db.py [csv_file_path]
"""

import asyncio
import sys
import os
import pandas as pd
import asyncpg

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Database configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'caelio_care',
    'user': 'postgres',
    'password': '123'  # Update this
}


async def import_books_to_db(csv_file: str):
    """
    Import books from CSV to database with duplicate checking
    
    Args:
        csv_file: Path to CSV file containing book data
    """
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return False
    
    print(f"📖 Reading CSV file: {csv_file}")
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"✅ Read {len(df)} books from CSV")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    # Verify required columns
    required_columns = ['product_id', 'title']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return False
    
    print("\n🔗 Connecting to database...")
    try:
        conn = await asyncpg.connect(**DATABASE_CONFIG)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        # Statistics
        inserted = 0
        skipped = 0
        errors = 0
        
        print(f"\n🚀 Starting import of {len(df)} books...")
        print("=" * 100)
        
        for idx, row in df.iterrows():
            title = str(row.get('title', ''))[:100]  # Limit title length
            
            # Convert product_id to integer
            try:
                product_id = int(row.get('product_id', 0))
            except (ValueError, TypeError):
                print(f"⚠️  [{idx+1:3d}] Skipped: Invalid product_id - {title[:50]}")
                skipped += 1
                continue
            
            if not product_id or pd.isna(row.get('product_id')):
                print(f"⚠️  [{idx+1:3d}] Skipped: No product_id - {title[:50]}")
                skipped += 1
                continue
            
            try:
                # Check if book already exists
                exists = await conn.fetchval(
                    'SELECT EXISTS(SELECT 1 FROM books WHERE product_id = $1)',
                    product_id
                )
                
                if exists:
                    print(f"⏭️  [{idx+1:3d}] Exists: {product_id:<15d} - {title[:60]}")
                    skipped += 1
                    continue
                
                # Prepare data for insertion
                authors = str(row.get('authors', '')) if pd.notna(row.get('authors')) else ''
                
                # Handle numeric fields
                original_price = float(row.get('original_price', 0)) if pd.notna(row.get('original_price')) else 0
                current_price = float(row.get('current_price', 0)) if pd.notna(row.get('current_price')) else 0
                quantity = float(row.get('quantity', 0)) if pd.notna(row.get('quantity')) else 0
                n_review = int(row.get('n_review', 0)) if pd.notna(row.get('n_review')) else 0
                avg_rating = float(row.get('avg_rating', 0)) if pd.notna(row.get('avg_rating')) else 0
                pages = int(row.get('pages', 0)) if pd.notna(row.get('pages')) else 0
                
                # Handle text fields
                category = str(row.get('category', '')) if pd.notna(row.get('category')) else ''
                manufacturer = str(row.get('manufacturer', '')) if pd.notna(row.get('manufacturer')) else ''
                cover_link = str(row.get('cover_link', '')) if pd.notna(row.get('cover_link')) else ''
                # summary = str(row.get('summary', '')) if pd.notna(row.get('summary')) else ''
                # content = str(row.get('content', '')) if pd.notna(row.get('content')) else ''
                
                # Insert book
                await conn.execute('''
                    INSERT INTO books (
                        product_id, title, authors, original_price, current_price,
                        quantity, category, n_review, avg_rating, pages,
                        manufacturer, cover_link
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ''',
                    product_id, title, authors, original_price, current_price,
                    quantity, category, n_review, avg_rating, pages,
                    manufacturer, cover_link
                )
                
                print(f"✅ [{idx+1:3d}] Inserted: {product_id:<15d} - {title[:60]}")
                inserted += 1
                
            except Exception as e:
                print(f"❌ [{idx+1:3d}] Error: {product_id:<15d} - {title[:50]} - {str(e)[:50]}")
                errors += 1
        
        # Print summary
        print("\n" + "=" * 100)
        print("📊 IMPORT SUMMARY:")
        print("=" * 100)
        print(f"✅ Inserted:  {inserted:>5d} books")
        print(f"⏭️  Skipped:   {skipped:>5d} books (already exist or no ID)")
        print(f"❌ Errors:    {errors:>5d} books")
        print(f"📚 Total:     {len(df):>5d} books in CSV")
        print("=" * 100)
        
        # Verify total books in database
        total_books = await conn.fetchval('SELECT COUNT(*) FROM books')
        print(f"\n📖 Total books in database: {total_books}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()
        print("\n✅ Database connection closed")


async def main():
    """Main function"""
    # Get CSV file path from command line or use default
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Default to merged book data
        csv_file = '../dataset/books_full_data.csv'
        print(f"ℹ️  No file specified, using default: {csv_file}")
    
    # Update database config from environment if available
    if 'DB_PASSWORD' in os.environ:
        DATABASE_CONFIG['password'] = os.environ['DB_PASSWORD']
    
    print("\n" + "=" * 100)
    print("📚 BOOK IMPORT TOOL")
    print("=" * 100)
    
    success = await import_books_to_db(csv_file)
    
    if success:
        print("\n🎉 Import completed successfully!")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
