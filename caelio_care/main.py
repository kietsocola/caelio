"""
Caelio Care API - Main FastAPI application
Emotional assessment and white books system
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
import asyncio
import json
import traceback
from contextlib import asynccontextmanager

# Local imports
from .database import init_database, get_db
from .auth import AuthManager, UserCreate, UserLogin, User, Token
from .emotional_system import EmotionalTestSystem, EmotionalAnswers, EmotionalProfile
from .white_books import (
    WhiteBooksManager, WhiteBookCreate, WhiteBook,
    ChapterCreate, Chapter, WhiteBookUpdate
)
from .bookstore import (
    BookstoreManager, BookstoreCreate, Bookstore,
    BookLinkCreate, BookLink,
    OrderCreate, Order, OrderItem
)

# Global variables
auth_manager = None
emotional_system = EmotionalTestSystem()
white_books_manager = None
bookstore_manager = None
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global auth_manager, white_books_manager, bookstore_manager
    
    # Initialize database
    await init_database()
    db_pool = await get_db()
    
    # Initialize managers
    auth_manager = AuthManager(db_pool)
    white_books_manager = WhiteBooksManager(db_pool)
    bookstore_manager = BookstoreManager(db_pool)
    
    print("Caelio Care API started successfully")
    yield
    
    # Shutdown
    print("Shutting down Caelio Care API")

# Create FastAPI app (without lifespan when mounted)
app = FastAPI(
    title="Caelio Care API",
    description="Emotional assessment and bibliotherapy system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize database when mounted
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    global auth_manager, white_books_manager, bookstore_manager
    
    try:
        # Initialize database
        await init_database()
        db_pool = await get_db()
        
        # Initialize managers
        auth_manager = AuthManager(db_pool)
        white_books_manager = WhiteBooksManager(db_pool)
        bookstore_manager = BookstoreManager(db_pool)
        
        # Import books from CSV
        from .database import import_books_from_csv
        await import_books_from_csv()
        
        print("✅ Caelio Care API initialized successfully")
    except Exception as e:
        print(f"❌ Caelio Care API initialization failed: {e}")
        # Don't fail completely, just log the error

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    global auth_manager
    
    # Ensure auth_manager is initialized
    if auth_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            auth_manager = AuthManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    token = credentials.credentials
    user_id = auth_manager.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth_manager.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def ensure_white_books_manager():
    """Ensure white books manager is initialized"""
    global white_books_manager
    
    if white_books_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            white_books_manager = WhiteBooksManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    return white_books_manager

# Optional dependency to get current user (no error if not authenticated)  
async def get_optional_current_user(request: Request) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    global auth_manager
    
    try:
        # Ensure auth_manager is initialized
        if auth_manager is None:
            await init_database()
            db_pool = await get_db()
            auth_manager = AuthManager(db_pool)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        user_id = auth_manager.verify_token(token)
        if not user_id:
            return None
        
        user = await auth_manager.get_user_by_id(user_id)
        return user
    except Exception:
        return None

# === BASIC ENDPOINTS ===

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Caelio Care API",
        "version": "1.0.0",
        "features": ["emotional_assessment", "white_books", "authentication"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Caelio Care API is running"}

# === AUTHENTICATION ENDPOINTS ===

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register new user"""
    global auth_manager
    
    # Ensure auth_manager is initialized
    if auth_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            auth_manager = AuthManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        user = await auth_manager.create_user(user_data)
        access_token = auth_manager.create_access_token(user.user_id)
        
        return Token(
            access_token=access_token,
            user=user
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user"""
    global auth_manager
    
    # Ensure auth_manager is initialized
    if auth_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            auth_manager = AuthManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    user = await auth_manager.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = auth_manager.create_access_token(user.user_id)
    return Token(
        access_token=access_token,
        user=user
    )

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

# === EMOTIONAL ASSESSMENT ENDPOINTS ===

@app.get("/emotional-test/questions")
async def get_emotional_questions():
    """Get emotional assessment questions"""
    return {
        "questions": emotional_system.questions,
        "scale": "1-5 (1 = Hoàn toàn không đồng ý, 5 = Hoàn toàn đồng ý)",
        "description": "Bộ câu hỏi đánh giá cảm xúc dựa trên mô hình PERMA-DASS"
    }

@app.post("/emotional-test/analyze", response_model=EmotionalProfile)
async def analyze_emotional_test(
    answers: EmotionalAnswers,
    request: Request,
    archetype: Optional[str] = None
):
    """Analyze emotional test results (no login required)"""
    try:
        # Validate answers (1-5 scale)
        answers_dict = answers.dict()
        for q_id, answer in answers_dict.items():
            if not (1 <= answer <= 5):
                raise HTTPException(status_code=400, detail=f"Answer for {q_id} must be between 1 and 5")
        
        # Calculate profile
        profile = emotional_system.calculate_emotional_profile(answers_dict, archetype)
        
        # Get optional user for saving results
        current_user = await get_optional_current_user(request)
        
        # Save result to database only if user is logged in
        if current_user:
            try:
                db_pool = await get_db()
                async with db_pool.acquire() as conn:
                    await conn.execute('''
                        INSERT INTO emotional_test_results (
                            user_id, answers, perma_score, dass_score, mbi_score, 
                            emotional_layer, archetype
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ''', 
                        current_user.user_id, json.dumps(answers_dict), profile.perma_score,
                        profile.dass_score, profile.mbi_score, profile.emotional_layer, 
                        archetype if archetype else None
                    )
            except Exception as e:
                # If saving fails, continue without error
                print(f"Failed to save test result: {e}")
        
        return profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing emotional test: {str(e)}")

@app.get("/emotional-test/prescription/{emotional_layer}")
async def get_book_prescription(emotional_layer: str, archetype: Optional[str] = None):
    """Get book prescription for emotional layer"""
    try:
        prescription = emotional_system.get_book_prescription(emotional_layer, archetype)
        return prescription
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prescription: {str(e)}")

@app.get("/emotional-test/my-results")
async def get_my_emotional_results(current_user: User = Depends(get_current_user)):
    """Get user's emotional test history"""
    try:
        db_pool = await get_db()
        async with db_pool.acquire() as conn:
            results = await conn.fetch('''
                SELECT 
                    result_id,
                    answers,
                    perma_score,
                    dass_score,
                    mbi_score,
                    emotional_layer,
                    archetype,
                    created_at
                FROM emotional_test_results
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 20
            ''', current_user.user_id)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "result_id": result['result_id'],
                    "answers": result['answers'],  # JSONB already parsed
                    "perma_score": float(result['perma_score']),
                    "dass_score": float(result['dass_score']),
                    "mbi_score": float(result['mbi_score']),
                    "emotional_layer": result['emotional_layer'],
                    "archetype": result['archetype'],
                    "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                    "interpretation": {
                        "perma": "Positive" if result['perma_score'] >= 3.5 else "Moderate" if result['perma_score'] >= 2.5 else "Low",
                        "dass": "High stress" if result['dass_score'] >= 3.0 else "Moderate stress" if result['dass_score'] >= 2.0 else "Low stress",
                        "mbi": "Burnout risk" if result['mbi_score'] >= 3.5 else "Moderate" if result['mbi_score'] >= 2.5 else "Good"
                    }
                })
            
            return {
                "total": len(formatted_results),
                "results": formatted_results
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")

# === WHITE BOOKS ENDPOINTS ===

@app.post("/white-books/create", response_model=WhiteBook)
async def create_white_book(
    book_data: WhiteBookCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new white book with metadata (title, cover, description)"""
    global white_books_manager
    
    # Ensure white_books_manager is initialized
    if white_books_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            white_books_manager = WhiteBooksManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        book = await white_books_manager.create_book(current_user.user_id, book_data)
        if book is None:
            raise HTTPException(status_code=500, detail="Book creation returned None - database might not have been updated")
        return book
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")

@app.get("/white-books/my-books", response_model=List[WhiteBook])
async def get_my_white_books(current_user: User = Depends(get_current_user)):
    """Get user's white books"""
    manager = await ensure_white_books_manager()
    try:
        books = await manager.get_user_books(current_user.user_id)
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting books: {str(e)}")

@app.put("/white-books/{book_id}/publish")
async def publish_white_book(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Publish a white book"""
    manager = await ensure_white_books_manager()
    try:
        success = await manager.publish_book(book_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        
        return {"message": "Book published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing book: {str(e)}")

@app.get("/white-books/published", response_model=List[WhiteBook])
async def get_published_white_books(
    emotional_layer: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Get published white books"""
    manager = await ensure_white_books_manager()
    try:
        offset = (page - 1) * page_size
        books = await manager.get_published_books(
            emotional_layer=emotional_layer,
            limit=page_size,
            offset=offset
        )
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting published books: {str(e)}")

@app.get("/white-books/{book_id}", response_model=WhiteBook)
async def get_white_book_detail(book_id: int, include_chapters: bool = True):
    """Get white book detail with optional chapters"""
    manager = await ensure_white_books_manager()
    try:
        book = await manager.get_book_by_id(book_id, include_author=True, include_chapters=include_chapters)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book.is_published:
            # Increment view count for published books
            await manager.increment_views(book_id)
        
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book detail: {str(e)}")

@app.put("/white-books/{book_id}", response_model=WhiteBook)
async def update_white_book(
    book_id: int,
    book_data: WhiteBookUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update white book metadata (title, cover_image, description, tags)"""
    manager = await ensure_white_books_manager()
    try:
        book = await manager.update_book(book_id, current_user.user_id, book_data)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book: {str(e)}")

@app.post("/white-books/{book_id}/chapters", response_model=Chapter)
async def add_chapter_to_book(
    book_id: int,
    chapter_data: ChapterCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new chapter to a white book"""
    manager = await ensure_white_books_manager()
    try:
        # Verify book ownership
        book = await manager.get_book_by_id(book_id, include_chapters=False)
        if not book or book.author_id != current_user.user_id:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        
        chapter = await manager.add_chapter(book_id, current_user.user_id, chapter_data)
        return chapter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding chapter: {str(e)}")

@app.get("/white-books/{book_id}/chapters", response_model=List[Chapter])
async def get_book_chapters(book_id: int):
    """Get all chapters of a white book"""
    manager = await ensure_white_books_manager()
    try:
        chapters = await manager.get_book_chapters(book_id)
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chapters: {str(e)}")

@app.delete("/white-books/{book_id}/chapters/{chapter_id}")
async def delete_chapter(
    book_id: int,
    chapter_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a chapter from a white book"""
    manager = await ensure_white_books_manager()
    try:
        # Verify book ownership
        book = await manager.get_book_by_id(book_id, include_chapters=False)
        if not book or book.author_id != current_user.user_id:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        
        success = await manager.delete_chapter(chapter_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chapter not found or not authorized")
        
        return {"message": "Chapter deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chapter: {str(e)}")

@app.put("/white-books/{book_id}/unpublish")
async def unpublish_white_book(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Unpublish a white book"""
    manager = await ensure_white_books_manager()
    try:
        success = await manager.unpublish_book(book_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        
        return {"message": "Book unpublished successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unpublishing book: {str(e)}")

@app.delete("/white-books/{book_id}")
async def delete_white_book(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a white book and all its chapters"""
    manager = await ensure_white_books_manager()
    try:
        success = await manager.delete_book(book_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Book not found or not authorized")
        
        return {"message": "Book deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting book: {str(e)}")

@app.post("/white-books/{book_id}/like")
async def toggle_like_white_book(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Toggle like on a white book"""
    manager = await ensure_white_books_manager()
    try:
        result = await manager.toggle_like(book_id, current_user.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling like: {str(e)}")


@app.get("/white-books/search/{query}", response_model=List[WhiteBook])
async def search_white_books(query: str, limit: int = 20):
    """Search white books"""
    manager = await ensure_white_books_manager()
    try:
        books = await manager.search_books(query, limit)
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching books: {str(e)}")

# === WRITING PROMPTS ENDPOINTS ===

@app.get("/writing-prompts/{emotional_layer}")
async def get_writing_prompts(emotional_layer: str):
    """Get writing prompts for emotional layer"""
    try:
        prescription = emotional_system.get_book_prescription(emotional_layer)
        return {
            "emotional_layer": emotional_layer,
            "prompts": prescription["writing_prompts"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting writing prompts: {str(e)}")

# === STATISTICS ENDPOINTS ===

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        db_pool = await get_db()
        async with db_pool.acquire() as conn:
            # Get user count
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            # Get emotional test count
            test_count = await conn.fetchval("SELECT COUNT(*) FROM emotional_test_results")
            
            # Get white books count
            books_count = await conn.fetchval("SELECT COUNT(*) FROM white_books")
            published_books_count = await conn.fetchval("SELECT COUNT(*) FROM white_books WHERE is_published = TRUE")
            
            # Get layer distribution
            layer_distribution = await conn.fetch('''
                SELECT emotional_layer, COUNT(*) as count
                FROM emotional_test_results
                GROUP BY emotional_layer
                ORDER BY count DESC
            ''')
            
            return {
                "users": user_count,
                "emotional_tests": test_count,
                "white_books": {
                    "total": books_count,
                    "published": published_books_count
                },
                "emotional_layers": [dict(row) for row in layer_distribution],
                "available_layers": list(emotional_system.layer_prescriptions.keys())
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# === BOOKSTORE ENDPOINTS ===

@app.post("/bookstores/register", response_model=Bookstore)
async def register_bookstore(bookstore_data: BookstoreCreate):
    """Register a new bookstore"""
    global bookstore_manager
    
    # Ensure bookstore_manager is initialized
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        bookstore = await bookstore_manager.create_bookstore(bookstore_data)
        return bookstore
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bookstore registration failed: {str(e)}")

@app.get("/bookstores", response_model=List[Bookstore])
async def get_all_bookstores(active_only: bool = True):
    """Get all bookstores"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        bookstores = await bookstore_manager.get_all_bookstores(active_only)
        return bookstores
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookstores: {str(e)}")

@app.get("/bookstores/{bookstore_id}", response_model=Bookstore)
async def get_bookstore(bookstore_id: int):
    """Get bookstore details"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        bookstore = await bookstore_manager.get_bookstore_by_id(bookstore_id)
        if not bookstore:
            raise HTTPException(status_code=404, detail="Bookstore not found")
        return bookstore
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookstore: {str(e)}")

@app.post("/bookstores/book-links", response_model=BookLink)
async def add_book_link(link_data: BookLinkCreate):
    """Add a purchase link for a book (bookstore adds their selling link)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        link = await bookstore_manager.add_book_link(link_data)
        return link
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding book link: {str(e)}")

@app.get("/bookstores/{bookstore_id}/books")
async def get_bookstore_books(bookstore_id: int):
    """Get all books available at a bookstore"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        books = await bookstore_manager.get_bookstore_books(bookstore_id)
        return {"bookstore_id": bookstore_id, "books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookstore books: {str(e)}")

@app.get("/books/{book_id}/purchase-links")
async def get_book_purchase_links(
    book_id: int,
    user_latitude: Optional[float] = None,
    user_longitude: Optional[float] = None
):
    """
    Get purchase links for a book, prioritized by:
    1. Distance from user (if GPS coordinates provided)
    2. Commission rate (higher = better)
    """
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        links = await bookstore_manager.get_book_links(
            book_id,
            user_latitude,
            user_longitude
        )
        
        return {
            "book_id": book_id,
            "total_links": len(links),
            "purchase_links": links,
            "sorted_by": "distance and commission_rate" if user_latitude else "commission_rate only"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting purchase links: {str(e)}")

@app.get("/books/{book_id}")
async def get_book_info(book_id: int):
    """Get book information by product_id"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        book = await bookstore_manager.get_book_info(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book info: {str(e)}")

@app.get("/books/search/{query}")
async def search_books(query: str, limit: int = 20):
    """Search books by title, author, or category"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        books = await bookstore_manager.search_books(query, limit)
        return {
            "query": query,
            "total": len(books),
            "books": books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching books: {str(e)}")

# === BOOK LINK VIEW COUNT ===

@app.post("/book-links/{book_link_id}/view")
async def increment_book_link_view(book_link_id: int):
    """Increment view count for a book link"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        success = await bookstore_manager.increment_view_count(book_link_id)
        if not success:
            raise HTTPException(status_code=404, detail="Book link not found")
        return {"message": "View count incremented successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error incrementing view count: {str(e)}")

@app.get("/book-links/{book_link_id}")
async def get_book_link_detail(book_link_id: int):
    """Get book link detail with full information"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        book_link = await bookstore_manager.get_book_link_by_id(book_link_id)
        if not book_link:
            raise HTTPException(status_code=404, detail="Book link not found")
        return book_link
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book link: {str(e)}")

# === ORDER MANAGEMENT ===

@app.post("/orders/create", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new order (requires authentication)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        order = await bookstore_manager.create_order(current_user.user_id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@app.get("/orders/my-orders", response_model=List[Order])
async def get_my_orders(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get user's orders"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        offset = (page - 1) * page_size
        orders = await bookstore_manager.get_user_orders(current_user.user_id, page_size, offset)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting orders: {str(e)}")

@app.get("/orders/{order_id}", response_model=Order)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get order detail (user can only see their own orders)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        order = await bookstore_manager.get_order_by_id(order_id, current_user.user_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting order: {str(e)}")

@app.put("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Cancel order (only if status is pending or confirmed)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        success = await bookstore_manager.cancel_order(order_id, current_user.user_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot cancel this order")
        return {"message": "Order cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling order: {str(e)}")

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    order_status: Optional[str] = None,
    payment_status: Optional[str] = None
):
    """Update order status (for bookstore/admin use)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        order = await bookstore_manager.update_order_status(order_id, order_status, payment_status)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")

@app.get("/bookstores/{bookstore_id}/orders", response_model=List[Order])
async def get_bookstore_orders(
    bookstore_id: int,
    page: int = 1,
    page_size: int = 50
):
    """Get bookstore orders (for bookstore management)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        offset = (page - 1) * page_size
        orders = await bookstore_manager.get_bookstore_orders(bookstore_id, page_size, offset)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookstore orders: {str(e)}")

@app.get("/bookstores/{bookstore_id}/statistics")
async def get_bookstore_statistics(bookstore_id: int):
    """Get bookstore statistics (sales, views, top books, etc.)"""
    global bookstore_manager
    
    if bookstore_manager is None:
        try:
            await init_database()
            db_pool = await get_db()
            bookstore_manager = BookstoreManager(db_pool)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    
    try:
        stats = await bookstore_manager.get_bookstore_statistics(bookstore_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)