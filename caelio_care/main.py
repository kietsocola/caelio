"""
Caelio Care API - Main FastAPI application
Emotional assessment and white books system
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
import asyncio
from contextlib import asynccontextmanager

# Local imports
from .database import init_database, get_db
from .auth import AuthManager, UserCreate, UserLogin, User, Token
from .emotional_system import EmotionalTestSystem, EmotionalAnswers, EmotionalProfile
from .white_books import WhiteBooksManager, WhiteBookCreate, WhiteBook

# Global variables
auth_manager = None
emotional_system = EmotionalTestSystem()
white_books_manager = None
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global auth_manager, white_books_manager
    
    # Initialize database
    await init_database()
    db_pool = await get_db()
    
    # Initialize managers
    auth_manager = AuthManager(db_pool)
    white_books_manager = WhiteBooksManager(db_pool)
    
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
    global auth_manager, white_books_manager
    
    try:
        # Initialize database
        await init_database()
        db_pool = await get_db()
        
        # Initialize managers
        auth_manager = AuthManager(db_pool)
        white_books_manager = WhiteBooksManager(db_pool)
        
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
                        current_user.id, answers_dict, profile.perma_score,
                        profile.dass_score, profile.mbi_score, profile.emotional_layer, archetype
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
                SELECT * FROM emotional_test_results
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 10
            ''', current_user.user_id)
            
            return [dict(result) for result in results]
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")

# === WHITE BOOKS ENDPOINTS ===

@app.post("/white-books/create", response_model=WhiteBook)
async def create_white_book(
    book_data: WhiteBookCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new white book"""
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
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating book: {str(e)}")

@app.get("/white-books/my-books", response_model=List[WhiteBook])
async def get_my_white_books(current_user: User = Depends(get_current_user)):
    """Get user's white books"""
    try:
        books = await white_books_manager.get_user_books(current_user.user_id)
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting books: {str(e)}")

@app.put("/white-books/{book_id}/publish")
async def publish_white_book(
    book_id: int,
    current_user: User = Depends(get_current_user)
):
    """Publish a white book"""
    try:
        success = await white_books_manager.publish_book(book_id, current_user.user_id)
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
    try:
        offset = (page - 1) * page_size
        books = await white_books_manager.get_published_books(
            emotional_layer=emotional_layer,
            limit=page_size,
            offset=offset
        )
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting published books: {str(e)}")

@app.get("/white-books/{book_id}", response_model=WhiteBook)
async def get_white_book_detail(book_id: int):
    """Get white book detail"""
    try:
        book = await white_books_manager.get_book_by_id(book_id, include_author=True)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book.is_published:
            # Increment view count for published books
            await white_books_manager.increment_views(book_id)
        
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book detail: {str(e)}")

@app.get("/white-books/search/{query}", response_model=List[WhiteBook])
async def search_white_books(query: str, limit: int = 20):
    """Search white books"""
    try:
        books = await white_books_manager.search_books(query, limit)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)