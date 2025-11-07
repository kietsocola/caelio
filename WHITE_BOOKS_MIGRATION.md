# White Books Migration Guide - Chapter-Based Structure

## Overview
The White Books system has been completely restructured to support multi-chapter books instead of a single content field. This allows users to create proper books with:
- **Book metadata**: title, cover_image, description, emotional_layer, tags
- **Multiple chapters**: Each with chapter_number, chapter_title, and content

---

## What Changed

### 1. Database Schema

**OLD Structure** (white_books table):
```sql
CREATE TABLE white_books (
    book_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    content TEXT,  -- Single large text field
    emotional_layer TEXT,
    is_published BOOLEAN,
    created_at TIMESTAMP
);
```

**NEW Structure** (2 tables):
```sql
-- Books table (metadata only)
CREATE TABLE white_books (
    id SERIAL PRIMARY KEY,  -- Changed from book_id
    author_id INTEGER,       -- Changed from user_id
    title TEXT NOT NULL,
    cover_image TEXT,        -- NEW
    description TEXT,        -- NEW
    emotional_layer TEXT,
    tags TEXT[],             -- NEW
    is_published BOOLEAN,
    view_count INTEGER,
    like_count INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP     -- NEW
);

-- Chapters table (separate)
CREATE TABLE white_book_chapters (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES white_books(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    chapter_title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(book_id, chapter_number)
);
```

**Key Changes**:
- ✅ `book_id` → `id`
- ✅ `user_id` → `author_id`
- ✅ Single `content` field → Multiple chapters in separate table
- ✅ Added `cover_image`, `description`, `tags`
- ✅ Added `view_count`, `like_count`, `updated_at`
- ✅ Chapters have unique `chapter_number` per book

---

### 2. Data Models (Pydantic)

**NEW Models**:
```python
class WhiteBookCreate(BaseModel):
    title: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    emotional_layer: str
    tags: Optional[List[str]] = None

class WhiteBookUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class Chapter(BaseModel):
    id: int
    book_id: int
    chapter_number: int
    chapter_title: str
    content: str
    created_at: datetime
    updated_at: datetime

class ChapterCreate(BaseModel):
    chapter_number: int
    chapter_title: str
    content: str

class WhiteBook(BaseModel):
    id: int
    author_id: int
    author_username: Optional[str] = None
    title: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    emotional_layer: str
    tags: Optional[List[str]] = None
    is_published: bool
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    chapters: Optional[List[Chapter]] = None  # Optional chapters list
```

---

### 3. API Endpoints

**NEW/Updated Endpoints**:

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/white-books/create` | Create book (metadata only) | Required |
| PUT | `/white-books/{book_id}` | Update book metadata | Required |
| POST | `/white-books/{book_id}/chapters` | Add chapter to book | Required |
| GET | `/white-books/{book_id}/chapters` | Get all chapters | Public |
| DELETE | `/white-books/{book_id}/chapters/{chapter_id}` | Delete chapter | Required |
| PUT | `/white-books/{book_id}/unpublish` | Unpublish book | Required |
| DELETE | `/white-books/{book_id}` | Delete book + chapters | Required |
| POST | `/white-books/{book_id}/like` | Toggle like | Required |
| GET | `/white-books/{book_id}?include_chapters=true` | Get book with/without chapters | Public |
| GET | `/white-books/my-books` | User's books | Required |
| GET | `/white-books/published` | Published books | Public |
| GET | `/white-books/search/{query}` | Search books | Public |
| PUT | `/white-books/{book_id}/publish` | Publish book | Required |

**Key Changes**:
- ✅ Create book now only creates metadata (no content)
- ✅ Add chapters separately via POST `/white-books/{book_id}/chapters`
- ✅ Update book via PUT `/white-books/{book_id}` (metadata only)
- ✅ GET book detail now has `include_chapters` parameter
- ✅ Added endpoints for unpublish, delete, like management

---

### 4. Manager Methods (white_books.py)

**All methods rewritten**:
- `create_book()` - Creates book metadata only
- `add_chapter()` - Add chapter to existing book
- `delete_chapter()` - Delete specific chapter
- `update_book()` - Update book metadata
- `get_book_by_id()` - Now supports `include_chapters` parameter
- `get_book_chapters()` - Get all chapters for a book
- `publish_book()` - Publish book
- `unpublish_book()` - NEW: Unpublish book
- `delete_book()` - DELETE book and all chapters (CASCADE)
- `toggle_like()` - NEW: Like/unlike functionality
- `increment_views()` - Increment view count

---

## Migration Steps

### Step 1: Backup Current Data
```bash
# Export current white_books table
pg_dump -U your_user -t white_books caelio_db > white_books_backup.sql
```

### Step 2: Run Migration Script
```bash
python update_white_books_schema.py
```

**What the script does**:
1. Creates backup table `white_books_old`
2. Creates new `white_books` table with new schema
3. Creates `white_book_chapters` table
4. Migrates existing books:
   - Copies metadata to new `white_books` table
   - Converts old `content` field to "Chapter 1" in `white_book_chapters`
   - Maps `book_id` → `id`, `user_id` → `author_id`
5. Creates indexes for performance
6. Keeps old data in `white_books_old` for safety

### Step 3: Verify Migration
```bash
# Connect to database
psql -U your_user -d caelio_db

# Check new tables
\dt white_books
\dt white_book_chapters
\dt white_books_old

# Verify data migration
SELECT COUNT(*) FROM white_books;
SELECT COUNT(*) FROM white_book_chapters;
SELECT COUNT(*) FROM white_books_old;

# Check a sample book
SELECT * FROM white_books WHERE id = 1;
SELECT * FROM white_book_chapters WHERE book_id = 1;
```

### Step 4: Test API
```bash
# Start the server
python run_api.py

# Test endpoints
curl http://localhost:8000/white-books/published
curl http://localhost:8000/white-books/1?include_chapters=true
```

---

## Usage Examples

### Old Way (Single Content)
```python
# Old: Create book with all content at once
POST /white-books/create
{
  "title": "My Book",
  "content": "Chapter 1...\n\nChapter 2...\n\nChapter 3...",
  "emotional_layer": "Layer 1"
}
```

### New Way (Multi-Chapter)
```python
# Step 1: Create book (metadata)
POST /white-books/create
Authorization: Bearer <token>
{
  "title": "My Book",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A book about healing",
  "emotional_layer": "Layer 1",
  "tags": ["healing", "hope"]
}
# Response: { "id": 123, ... }

# Step 2: Add Chapter 1
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started..."
}

# Step 3: Add Chapter 2
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 2,
  "chapter_title": "The Journey",
  "content": "Days passed..."
}

# Step 4: Add Chapter 3
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 3,
  "chapter_title": "The Healing",
  "content": "Finally..."
}

# Step 5: Publish
PUT /white-books/123/publish
Authorization: Bearer <token>
```

---

## Benefits

### For Users
✅ **Structured content**: Chapters are clearly separated  
✅ **Better organization**: Add, edit, delete individual chapters  
✅ **Book metadata**: Cover image, description, tags  
✅ **Flexible ordering**: Add chapters in any order  
✅ **Better UX**: Table of contents, chapter navigation

### For System
✅ **Better performance**: Load metadata without full content  
✅ **Easier editing**: Update specific chapters without reloading entire book  
✅ **Analytics**: Track views, likes per book  
✅ **Search**: Index chapters separately for better search results  
✅ **Scalability**: No single huge text field

---

## Important Notes

### Data Integrity
- ✅ Old data is preserved in `white_books_old` table
- ✅ Migration creates Chapter 1 from old content field
- ✅ All foreign keys use CASCADE on delete
- ✅ UNIQUE constraint on (book_id, chapter_number) prevents duplicates

### Breaking Changes
⚠️ **API Changes**:
- `book_id` is now `id` in WhiteBook model
- `user_id` is now `author_id` in WhiteBook model
- `content` field removed from WhiteBook model
- Create endpoint no longer accepts `content`
- GET book detail returns chapters in `chapters` array (optional)

⚠️ **Frontend Impact**:
- Update all API calls to use new endpoints
- Book creation is now 2-step (create + add chapters)
- Display chapters as list instead of single text
- Add chapter management UI (add, edit, delete chapters)

### Rollback Plan
If needed to rollback:
```sql
-- Restore old table
DROP TABLE white_book_chapters;
DROP TABLE white_books;
ALTER TABLE white_books_old RENAME TO white_books;
```

---

## Testing Checklist

- [ ] Run migration script successfully
- [ ] Verify data migration (counts match)
- [ ] Test creating new book with chapters
- [ ] Test adding chapters to existing book
- [ ] Test updating book metadata
- [ ] Test deleting chapters
- [ ] Test publishing/unpublishing books
- [ ] Test deleting entire book
- [ ] Test viewing published books
- [ ] Test search functionality
- [ ] Test like/unlike functionality
- [ ] Test getting book with/without chapters
- [ ] Verify old books still work (migrated as Chapter 1)

---

## Documentation

- **Full API Docs**: `WHITE_BOOKS_API_DOCS.md`
- **Combined API Docs**: `API_COMPLETE_DOCUMENTATION.md`
- **Database Schema**: `caelio_care/database.py`
- **Models**: `caelio_care/white_books.py`
- **Endpoints**: `caelio_care/main.py`

---

## Support

For issues or questions about the migration, contact the development team.
