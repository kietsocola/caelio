# White Books API Documentation

## Overview
White Books is a user-generated content system where users can write and publish their own books with multiple chapters. Books are structured with metadata (title, cover, description) and contain multiple chapters that are ordered sequentially.

**Base URL**: `/white-books`

---

## Data Models

### WhiteBook
```json
{
  "id": 1,
  "author_id": 123,
  "author_username": "john_doe",
  "title": "My Journey to Happiness",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A personal story about overcoming anxiety",
  "emotional_layer": "Layer 1",
  "tags": ["anxiety", "self-help", "mindfulness"],
  "is_published": true,
  "view_count": 245,
  "like_count": 18,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-20T14:22:00",
  "chapters": [...]  // Optional, see Chapter model
}
```

### Chapter
```json
{
  "id": 1,
  "book_id": 1,
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started on a rainy Monday morning...",
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### WhiteBookCreate
```json
{
  "title": "My Journey to Happiness",
  "cover_image": "https://example.com/cover.jpg",  // Optional
  "description": "A personal story about overcoming anxiety",
  "emotional_layer": "Layer 1",
  "tags": ["anxiety", "self-help", "mindfulness"]  // Optional
}
```

### WhiteBookUpdate
```json
{
  "title": "Updated Title",  // Optional
  "cover_image": "https://example.com/new-cover.jpg",  // Optional
  "description": "Updated description",  // Optional
  "tags": ["new", "tags"]  // Optional
}
```

### ChapterCreate
```json
{
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started on a rainy Monday morning..."
}
```

---

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

**Public Endpoints** (no auth required):
- GET `/white-books/published` - View published books
- GET `/white-books/{book_id}` - View book details
- GET `/white-books/{book_id}/chapters` - View book chapters
- GET `/white-books/search/{query}` - Search books

**Protected Endpoints** (auth required):
- All create, update, delete operations
- User's own books management

---

## API Endpoints

### 1. Create White Book
Create a new white book with metadata.

**Endpoint**: `POST /white-books/create`  
**Auth**: Required  
**Request Body**:
```json
{
  "title": "My Journey to Happiness",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A personal story about overcoming anxiety",
  "emotional_layer": "Layer 1",
  "tags": ["anxiety", "self-help", "mindfulness"]
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "author_id": 123,
  "author_username": "john_doe",
  "title": "My Journey to Happiness",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A personal story about overcoming anxiety",
  "emotional_layer": "Layer 1",
  "tags": ["anxiety", "self-help", "mindfulness"],
  "is_published": false,
  "view_count": 0,
  "like_count": 0,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "chapters": []
}
```

**Notes**: 
- Book is created as unpublished by default
- No chapters included initially - add them separately
- `emotional_layer` should match PERMA-DASS layers

---

### 2. Update White Book
Update book metadata (title, cover, description, tags).

**Endpoint**: `PUT /white-books/{book_id}`  
**Auth**: Required (must be book author)  
**Request Body**:
```json
{
  "title": "Updated Title",
  "cover_image": "https://example.com/new-cover.jpg",
  "description": "Updated description",
  "tags": ["new", "tags"]
}
```

**Response**: `200 OK` - Returns updated WhiteBook object

**Errors**:
- `404` - Book not found or user not authorized

---

### 3. Add Chapter to Book
Add a new chapter to a white book.

**Endpoint**: `POST /white-books/{book_id}/chapters`  
**Auth**: Required (must be book author)  
**Request Body**:
```json
{
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started on a rainy Monday morning when I realized..."
}
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "book_id": 1,
  "chapter_number": 1,
  "chapter_title": "The Beginning",
  "content": "It all started on a rainy Monday morning...",
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

**Notes**:
- `chapter_number` must be unique within the book
- Chapters are automatically ordered by `chapter_number`
- You can add chapters in any order (e.g., chapter 3 before chapter 2)

---

### 4. Get Book Chapters
Get all chapters of a specific book.

**Endpoint**: `GET /white-books/{book_id}/chapters`  
**Auth**: Not required  
**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "book_id": 1,
    "chapter_number": 1,
    "chapter_title": "The Beginning",
    "content": "It all started...",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": "2024-01-15T10:35:00"
  },
  {
    "id": 2,
    "book_id": 1,
    "chapter_number": 2,
    "chapter_title": "The Struggle",
    "content": "Days turned into weeks...",
    "created_at": "2024-01-15T11:20:00",
    "updated_at": "2024-01-15T11:20:00"
  }
]
```

**Notes**: Chapters are sorted by `chapter_number` ascending

---

### 5. Delete Chapter
Delete a specific chapter from a book.

**Endpoint**: `DELETE /white-books/{book_id}/chapters/{chapter_id}`  
**Auth**: Required (must be book author)  
**Response**: `200 OK`
```json
{
  "message": "Chapter deleted successfully"
}
```

**Errors**:
- `404` - Book not found, chapter not found, or user not authorized

---

### 6. Get My Books
Get all books created by the current user.

**Endpoint**: `GET /white-books/my-books`  
**Auth**: Required  
**Response**: `200 OK` - Array of WhiteBook objects (includes both published and unpublished)

---

### 7. Get Book Detail
Get detailed information about a specific book.

**Endpoint**: `GET /white-books/{book_id}?include_chapters=true`  
**Auth**: Not required  
**Query Parameters**:
- `include_chapters` (boolean, default: true) - Include chapters in response

**Response**: `200 OK` - WhiteBook object with chapters

**Notes**:
- View count is automatically incremented for published books
- Use `include_chapters=false` to get metadata only

---

### 8. Publish Book
Publish a white book to make it publicly visible.

**Endpoint**: `PUT /white-books/{book_id}/publish`  
**Auth**: Required (must be book author)  
**Response**: `200 OK`
```json
{
  "message": "Book published successfully"
}
```

**Notes**:
- Only published books appear in public listings
- Published books can be found via search

---

### 9. Unpublish Book
Unpublish a white book to hide it from public view.

**Endpoint**: `PUT /white-books/{book_id}/unpublish`  
**Auth**: Required (must be book author)  
**Response**: `200 OK`
```json
{
  "message": "Book unpublished successfully"
}
```

**Notes**:
- Unpublished books are only visible to the author
- View count and likes are preserved

---

### 10. Delete Book
Permanently delete a white book and all its chapters.

**Endpoint**: `DELETE /white-books/{book_id}`  
**Auth**: Required (must be book author)  
**Response**: `200 OK`
```json
{
  "message": "Book deleted successfully"
}
```

**Notes**:
- This action cannot be undone
- All chapters are deleted automatically (CASCADE)

---

### 11. Get Published Books
Get all published white books with optional filtering.

**Endpoint**: `GET /white-books/published?emotional_layer=Layer1&page=1&page_size=20`  
**Auth**: Not required  
**Query Parameters**:
- `emotional_layer` (string, optional) - Filter by emotional layer
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20) - Items per page

**Response**: `200 OK` - Array of WhiteBook objects

**Example**:
```bash
# Get all published books
GET /white-books/published

# Get Layer 1 books, page 2
GET /white-books/published?emotional_layer=Layer 1&page=2&page_size=10
```

---

### 12. Search Books
Search published books by title, description, or tags.

**Endpoint**: `GET /white-books/search/{query}?limit=20`  
**Auth**: Not required  
**Query Parameters**:
- `limit` (int, default: 20) - Maximum results

**Response**: `200 OK` - Array of matching WhiteBook objects

**Example**:
```bash
GET /white-books/search/anxiety?limit=10
```

**Notes**:
- Searches in title, description, tags, and author username
- Only searches published books
- Case-insensitive partial matching

---

### 13. Toggle Like
Like or unlike a white book.

**Endpoint**: `POST /white-books/{book_id}/like`  
**Auth**: Required  
**Response**: `200 OK`
```json
{
  "liked": true,
  "like_count": 19
}
```

**Notes**:
- First call adds a like
- Second call removes the like (toggle)
- Returns current like status and total count

---

## Complete Usage Flow

### Creating a Multi-Chapter Book

```bash
# 1. Create the book
POST /white-books/create
Authorization: Bearer <token>
{
  "title": "My Healing Journey",
  "cover_image": "https://example.com/cover.jpg",
  "description": "A 5-chapter story about overcoming depression",
  "emotional_layer": "Layer 1",
  "tags": ["depression", "recovery", "hope"]
}
# Response: { "id": 123, ... }

# 2. Add Chapter 1
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 1,
  "chapter_title": "The Dark Days",
  "content": "It started in the winter of 2020..."
}

# 3. Add Chapter 2
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 2,
  "chapter_title": "Finding Help",
  "content": "The turning point came when..."
}

# 4. Add more chapters (3, 4, 5...)

# 5. Review the full book
GET /white-books/123?include_chapters=true

# 6. Publish when ready
PUT /white-books/123/publish
Authorization: Bearer <token>

# 7. Book is now publicly visible
GET /white-books/published?emotional_layer=Layer 1
```

### Editing an Existing Book

```bash
# 1. Update book metadata
PUT /white-books/123
Authorization: Bearer <token>
{
  "title": "Updated Title",
  "description": "New description"
}

# 2. Delete a chapter
DELETE /white-books/123/chapters/456
Authorization: Bearer <token>

# 3. Add a new chapter
POST /white-books/123/chapters
Authorization: Bearer <token>
{
  "chapter_number": 6,
  "chapter_title": "New Chapter",
  "content": "Additional content..."
}

# 4. Unpublish to make changes private
PUT /white-books/123/unpublish
Authorization: Bearer <token>
```

---

## Error Responses

All endpoints may return these error codes:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Resource not found or user not authorized
- **500 Internal Server Error**: Server error

**Error Response Format**:
```json
{
  "detail": "Error message description"
}
```

---

## Database Schema

### white_books Table
```sql
CREATE TABLE white_books (
    id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users(user_id),
    title TEXT NOT NULL,
    cover_image TEXT,
    description TEXT,
    emotional_layer TEXT,
    tags TEXT[],
    is_published BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_white_books_author ON white_books(author_id);
CREATE INDEX idx_white_books_published ON white_books(is_published);
CREATE INDEX idx_white_books_layer ON white_books(emotional_layer);
```

### white_book_chapters Table
```sql
CREATE TABLE white_book_chapters (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES white_books(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    chapter_title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book_id, chapter_number)
);

CREATE INDEX idx_chapters_book ON white_book_chapters(book_id);
```

### white_book_likes Table
```sql
CREATE TABLE white_book_likes (
    book_id INTEGER NOT NULL REFERENCES white_books(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, user_id)
);
```

---

## Migration from Old Schema

If upgrading from the old single-content white books system, run:

```bash
python update_white_books_schema.py
```

This will:
1. Backup existing data
2. Create new tables with chapter support
3. Migrate old books (content becomes Chapter 1)
4. Preserve all metadata (likes, views, etc.)

---

## Notes for Frontend Developers

### Book Creation Flow
1. Create book with metadata → Get `book_id`
2. Add chapters one by one (can be in any order)
3. Preview using GET with `include_chapters=true`
4. Publish when ready

### Chapter Management
- Chapters can be added in any order (chapter 3 before chapter 1 is OK)
- `chapter_number` must be unique per book
- Frontend should sort by `chapter_number` for display
- Delete individual chapters without affecting the book

### Performance Considerations
- Use `include_chapters=false` when only metadata is needed
- Pagination is built-in for published books listing
- Search results are limited (default 20, max via query param)

### Emotional Layer Values
Valid values (from PERMA-DASS system):
- "Layer 1" - High stress, low wellbeing
- "Layer 2" - Moderate stress, moderate wellbeing
- "Layer 3" - Low stress, high wellbeing
- "Layer 4" - Balanced wellbeing

### Tags
- Optional array of strings
- Searchable via `/search` endpoint
- Frontend can suggest common tags or allow free-form input
