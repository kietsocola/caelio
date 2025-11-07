# White Books API - Frontend Quick Reference

## TL;DR
Books now have **chapters** instead of single content field. Create book → Add chapters → Publish.

---

## Quick Start

### 1. Create a Book with Chapters

```javascript
// Step 1: Create book (metadata only)
const createResponse = await fetch('http://localhost:8000/white-books/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    title: "My Healing Journey",
    cover_image: "https://example.com/cover.jpg",
    description: "A personal story about recovery",
    emotional_layer: "Layer 1",
    tags: ["healing", "hope", "recovery"]
  })
});
const book = await createResponse.json();
// { id: 123, title: "My Healing Journey", ... }

// Step 2: Add Chapter 1
await fetch(`http://localhost:8000/white-books/${book.id}/chapters`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    chapter_number: 1,
    chapter_title: "The Dark Days",
    content: "It all started when..."
  })
});

// Step 3: Add Chapter 2
await fetch(`http://localhost:8000/white-books/${book.id}/chapters`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    chapter_number: 2,
    chapter_title: "Finding Hope",
    content: "The turning point came when..."
  })
});

// Step 4: Publish the book
await fetch(`http://localhost:8000/white-books/${book.id}/publish`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
```

### 2. Display a Book with Chapters

```javascript
// Get book with chapters
const response = await fetch(`http://localhost:8000/white-books/123?include_chapters=true`);
const book = await response.json();

// Display in React/Vue
function BookViewer({ book }) {
  return (
    <div>
      <img src={book.cover_image} alt={book.title} />
      <h1>{book.title}</h1>
      <p>{book.description}</p>
      <div>Tags: {book.tags.join(', ')}</div>
      
      <div>
        <h2>Chapters</h2>
        {book.chapters.map(chapter => (
          <div key={chapter.id}>
            <h3>Chapter {chapter.chapter_number}: {chapter.chapter_title}</h3>
            <p>{chapter.content}</p>
          </div>
        ))}
      </div>
      
      <div>
        Views: {book.view_count} | Likes: {book.like_count}
      </div>
    </div>
  );
}
```

### 3. Edit Book & Chapters

```javascript
// Update book metadata
await fetch(`http://localhost:8000/white-books/123`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    title: "Updated Title",
    description: "New description",
    tags: ["new", "tags"]
  })
});

// Delete a chapter
await fetch(`http://localhost:8000/white-books/123/chapters/456`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});

// Add a new chapter
await fetch(`http://localhost:8000/white-books/123/chapters`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify({
    chapter_number: 3,
    chapter_title: "New Chapter",
    content: "More content..."
  })
});
```

---

## Common Patterns

### Browse Published Books
```javascript
// Get all published books (with pagination)
const response = await fetch('http://localhost:8000/white-books/published?page=1&page_size=20');
const books = await response.json();

// Filter by emotional layer
const layer1Books = await fetch('http://localhost:8000/white-books/published?emotional_layer=Layer 1');
```

### Search Books
```javascript
const results = await fetch('http://localhost:8000/white-books/search/healing?limit=10');
const matchingBooks = await results.json();
```

### Like/Unlike a Book
```javascript
const response = await fetch(`http://localhost:8000/white-books/123/like`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
const result = await response.json();
// { liked: true, like_count: 19 }
```

### Get User's Books
```javascript
const response = await fetch('http://localhost:8000/white-books/my-books', {
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
const myBooks = await response.json();
```

### Delete Book
```javascript
// Deletes book and ALL chapters (cannot be undone)
await fetch(`http://localhost:8000/white-books/123`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
```

---

## Data Models (TypeScript)

```typescript
interface WhiteBook {
  id: number;
  author_id: number;
  author_username?: string;
  title: string;
  cover_image?: string;
  description?: string;
  emotional_layer: string;
  tags?: string[];
  is_published: boolean;
  view_count: number;
  like_count: number;
  created_at: string;  // ISO 8601 datetime
  updated_at: string;
  chapters?: Chapter[];  // Only included if requested
}

interface Chapter {
  id: number;
  book_id: number;
  chapter_number: number;
  chapter_title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

interface WhiteBookCreate {
  title: string;
  cover_image?: string;
  description?: string;
  emotional_layer: string;
  tags?: string[];
}

interface WhiteBookUpdate {
  title?: string;
  cover_image?: string;
  description?: string;
  tags?: string[];
}

interface ChapterCreate {
  chapter_number: number;
  chapter_title: string;
  content: string;
}
```

---

## UI Components Needed

### Book Creation Form
```
1. Book Info Form
   - Title (required)
   - Cover Image URL (optional)
   - Description (optional)
   - Emotional Layer (dropdown: Layer 1-4)
   - Tags (chips input)
   - [Create Book] button

2. Chapter Editor (after book created)
   - Chapter Number (number input)
   - Chapter Title (text input)
   - Content (rich text editor)
   - [Add Chapter] button
   - Chapter List (with edit/delete)

3. Preview & Publish
   - Show book with all chapters
   - [Publish] button
```

### Book Reader
```
- Cover image
- Title, author, description
- Tags
- View count, like count
- Table of contents (clickable chapter links)
- Chapter content (paginated or scrollable)
- Like button
- Share button
```

### My Books Dashboard
```
- List of user's books
- Show: cover, title, published status, views, likes
- Actions: Edit, Unpublish, Delete
- [Create New Book] button
```

### Chapter Manager
```
- List chapters by number
- Drag-to-reorder (update chapter_number)
- Edit chapter (inline or modal)
- Delete chapter (confirm dialog)
- Add new chapter
```

---

## Validation Rules

### Book Creation
- ✅ `title`: Required, max 200 chars
- ✅ `cover_image`: Optional, must be valid URL
- ✅ `description`: Optional, max 1000 chars
- ✅ `emotional_layer`: Required, must be one of: "Layer 1", "Layer 2", "Layer 3", "Layer 4"
- ✅ `tags`: Optional array, max 10 tags

### Chapter Creation
- ✅ `chapter_number`: Required, must be positive integer, unique per book
- ✅ `chapter_title`: Required, max 200 chars
- ✅ `content`: Required, min 10 chars

---

## Error Handling

```javascript
async function createBook(bookData, token) {
  try {
    const response = await fetch('http://localhost:8000/white-books/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(bookData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      if (response.status === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/login';
      } else if (response.status === 400) {
        // Bad request - show validation errors
        alert(`Error: ${error.detail}`);
      } else {
        // Server error
        alert('Something went wrong. Please try again.');
      }
      return null;
    }
    
    return await response.json();
  } catch (err) {
    console.error('Network error:', err);
    alert('Network error. Please check your connection.');
    return null;
  }
}
```

---

## Performance Tips

### 1. Load Metadata First, Chapters Later
```javascript
// Fast: Get book list without chapters
const books = await fetch('/white-books/published?page=1').then(r => r.json());

// Then: Load chapters only when user clicks on a book
const fullBook = await fetch(`/white-books/${bookId}?include_chapters=true`).then(r => r.json());
```

### 2. Pagination
```javascript
function BookList({ page, pageSize = 20 }) {
  const [books, setBooks] = useState([]);
  
  useEffect(() => {
    fetch(`/white-books/published?page=${page}&page_size=${pageSize}`)
      .then(r => r.json())
      .then(setBooks);
  }, [page, pageSize]);
  
  // Render books with pagination controls
}
```

### 3. Lazy Load Chapters
```javascript
// Load chapters separately for better performance
const chapters = await fetch(`/white-books/${bookId}/chapters`).then(r => r.json());
```

---

## Complete Example: Book Creation Wizard

```javascript
import React, { useState } from 'react';

function BookCreationWizard({ userToken, onComplete }) {
  const [step, setStep] = useState(1);
  const [bookId, setBookId] = useState(null);
  const [bookData, setBookData] = useState({
    title: '',
    cover_image: '',
    description: '',
    emotional_layer: 'Layer 1',
    tags: []
  });
  const [chapters, setChapters] = useState([]);

  // Step 1: Create Book
  const createBook = async () => {
    const response = await fetch('http://localhost:8000/white-books/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}`
      },
      body: JSON.stringify(bookData)
    });
    const book = await response.json();
    setBookId(book.id);
    setStep(2);
  };

  // Step 2: Add Chapters
  const addChapter = async (chapterData) => {
    await fetch(`http://localhost:8000/white-books/${bookId}/chapters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}`
      },
      body: JSON.stringify(chapterData)
    });
    setChapters([...chapters, chapterData]);
  };

  // Step 3: Publish
  const publishBook = async () => {
    await fetch(`http://localhost:8000/white-books/${bookId}/publish`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${userToken}` }
    });
    onComplete(bookId);
  };

  if (step === 1) {
    return (
      <div>
        <h2>Step 1: Book Information</h2>
        <input
          type="text"
          placeholder="Title"
          value={bookData.title}
          onChange={e => setBookData({...bookData, title: e.target.value})}
        />
        <input
          type="text"
          placeholder="Cover Image URL"
          value={bookData.cover_image}
          onChange={e => setBookData({...bookData, cover_image: e.target.value})}
        />
        <textarea
          placeholder="Description"
          value={bookData.description}
          onChange={e => setBookData({...bookData, description: e.target.value})}
        />
        <select
          value={bookData.emotional_layer}
          onChange={e => setBookData({...bookData, emotional_layer: e.target.value})}
        >
          <option value="Layer 1">Layer 1</option>
          <option value="Layer 2">Layer 2</option>
          <option value="Layer 3">Layer 3</option>
          <option value="Layer 4">Layer 4</option>
        </select>
        <button onClick={createBook}>Next: Add Chapters</button>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div>
        <h2>Step 2: Add Chapters</h2>
        <ChapterList chapters={chapters} />
        <ChapterEditor onAdd={addChapter} nextNumber={chapters.length + 1} />
        <button onClick={() => setStep(3)} disabled={chapters.length === 0}>
          Next: Review & Publish
        </button>
      </div>
    );
  }

  if (step === 3) {
    return (
      <div>
        <h2>Step 3: Review & Publish</h2>
        <BookPreview bookData={bookData} chapters={chapters} />
        <button onClick={publishBook}>Publish Book</button>
      </div>
    );
  }
}
```

---

## Migration Notes for Frontend

### Old API (Single Content)
```javascript
// OLD: Create book with all content
POST /white-books/create
{
  "title": "My Book",
  "content": "All content in one field...",  // REMOVED
  "emotional_layer": "Layer 1"
}
```

### New API (Multi-Chapter)
```javascript
// NEW: Create book (metadata)
POST /white-books/create
{
  "title": "My Book",
  "cover_image": "...",     // NEW
  "description": "...",     // NEW
  "emotional_layer": "Layer 1",
  "tags": ["..."]           // NEW
}

// Then add chapters
POST /white-books/{book_id}/chapters
{
  "chapter_number": 1,      // NEW
  "chapter_title": "...",   // NEW
  "content": "..."
}
```

### Key Changes
- ⚠️ No more `content` field in book creation
- ⚠️ `book_id` → `id` in response
- ⚠️ `user_id` → `author_id` in response
- ✅ New fields: `cover_image`, `description`, `tags`
- ✅ New feature: chapters as separate entities
- ✅ New feature: like/unlike, view count

---

## Complete Endpoint List

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/white-books/create` | ✅ | Create book |
| PUT | `/white-books/{id}` | ✅ | Update book |
| DELETE | `/white-books/{id}` | ✅ | Delete book |
| POST | `/white-books/{id}/chapters` | ✅ | Add chapter |
| GET | `/white-books/{id}/chapters` | ❌ | Get chapters |
| DELETE | `/white-books/{id}/chapters/{cid}` | ✅ | Delete chapter |
| GET | `/white-books/{id}` | ❌ | Get book detail |
| PUT | `/white-books/{id}/publish` | ✅ | Publish book |
| PUT | `/white-books/{id}/unpublish` | ✅ | Unpublish book |
| POST | `/white-books/{id}/like` | ✅ | Like/unlike |
| GET | `/white-books/my-books` | ✅ | User's books |
| GET | `/white-books/published` | ❌ | Published books |
| GET | `/white-books/search/{query}` | ❌ | Search books |

---

## Questions?

- Full API docs: `WHITE_BOOKS_API_DOCS.md`
- Migration guide: `WHITE_BOOKS_MIGRATION.md`
- Complete API docs: `API_COMPLETE_DOCUMENTATION.md`
