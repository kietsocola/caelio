"""
Caelio Web API - REST API cho hệ thống phân loại tính cách đọc sách
Sử dụng FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import os
from caelio_personality_system import CaelioPersonalitySystem
from caelio_book_matcher import CaelioBookMatcher

# Khởi tạo FastAPI app
app = FastAPI(
    title="Caelio Personality API",
    description="API phân loại tính cách đọc sách và gợi ý sách phù hợp",
    version="1.0.0"
)

# CORS middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định cụ thể domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo hệ thống
personality_system = CaelioPersonalitySystem()
book_matcher = CaelioBookMatcher()

# === PYDANTIC MODELS ===

class PersonalityAnswers(BaseModel):
    """Model cho câu trả lời personality test - hành trình khám phá (3 hoặc 8 câu)"""
    Q1: str
    Q2: str
    Q3: str
    Q4: Optional[str] = None
    Q5: Optional[str] = None
    Q6: Optional[str] = None
    Q7: Optional[str] = None
    Q8: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example_short": {
                "Q1": "A",
                "Q2": "C", 
                "Q3": "E"
            },
            "example_full": {
                "Q1": "A",
                "Q2": "C", 
                "Q3": "E",
                "Q4": "C",
                "Q5": "B",
                "Q6": "E",
                "Q7": "C",
                "Q8": "C"
            }
        }

class ProfessionalAnswers(BaseModel):
    """Model cho câu trả lời hành trình chuyên ngành - 4 câu hỏi"""
    Q1: str  # Lĩnh vực muốn đào sâu
    Q2: str  # Mục tiêu đọc  
    Q3: str  # Phong cách học
    Q4: str  # Cách trình bày ưa thích
    
    class Config:
        schema_extra = {
            "example": {
                "Q1": "A",  # Kinh tế - Quản trị - Tài chính
                "Q2": "B",  # Giải quyết vấn đề thực tế
                "Q3": "B",  # Tự mình tìm liên kết (synthesizer potential)
                "Q4": "C"   # Kết nối đa ngành (synthesizer)
            }
        }

class CombinedAnswers(BaseModel):
    """Model cho câu trả lời cả 2 hành trình"""
    discovery_answers: PersonalityAnswers
    professional_answers: ProfessionalAnswers

class PersonalityProfile(BaseModel):
    """Model cho kết quả phân tích tính cách"""
    primary_group: str
    secondary_group: Optional[str]
    primary_score: int
    secondary_score: int
    synthesizer_score: int
    is_synthesizer: bool
    profile_name: str
    english_name: str
    all_scores: Dict[str, int]
    is_multi_motivated: bool
    description: Dict[str, str]
    
class ProfessionalProfile(BaseModel):
    """Model cho kết quả phân tích tính cách chuyên ngành"""
    # Kế thừa từ PersonalityProfile
    primary_group: str
    secondary_group: Optional[str]
    primary_score: int
    secondary_score: int
    synthesizer_score: int
    is_synthesizer: bool
    profile_name: str
    english_name: str
    all_scores: Dict[str, int]
    is_multi_motivated: bool
    description: Dict[str, str]
    
    # Thông tin chuyên ngành
    field: str
    motivation: str
    learning_style: str
    presentation_preference: str
    professional_synthesizer_indicators: int

class BookRecommendation(BaseModel):
    """Model cho gợi ý sách"""
    product_id: Any
    title: str
    authors: Optional[str]
    category: str
    summary: Optional[str]
    personality_match_score: float
    cover_link: Optional[str]

class RecommendationResult(BaseModel):
    """Model cho kết quả gợi ý tổng thể"""
    profile: PersonalityProfile
    recommendations: List[BookRecommendation]
    total_matches: int
    match_distribution: Dict[str, int]

class QuestionData(BaseModel):
    """Model cho câu hỏi"""
    question: str
    choices: Dict[str, Dict[str, Any]]  # Sử dụng Any thay vì str để hỗ trợ cả bool và str

class BookDetail(BaseModel):
    """Model cho thông tin chi tiết sách"""
    product_id: Any
    title: str
    authors: Optional[str]
    original_price: Optional[float]
    current_price: Optional[float]
    quantity: Optional[float]
    category: str
    n_review: Optional[int]
    avg_rating: Optional[float]
    pages: Optional[int]
    manufacturer: Optional[str]
    cover_link: Optional[str]
    summary: Optional[str]
    content: Optional[str]

class BookListItem(BaseModel):
    """Model cho item trong danh sách sách (không có content đầy đủ)"""
    product_id: Any
    title: str
    authors: Optional[str]
    original_price: Optional[float]
    current_price: Optional[float]
    category: str
    n_review: Optional[int]
    avg_rating: Optional[float]
    pages: Optional[int]
    manufacturer: Optional[str]
    cover_link: Optional[str]
    summary: Optional[str]

class BookListResponse(BaseModel):
    """Model cho response danh sách sách"""
    books: List[BookListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# === HELPER FUNCTIONS ===

def safe_string_value(value, default=''):
    """Safely convert value to string, handling NaN"""
    if pd.isna(value):
        return default
    return str(value) if value is not None else default

def create_book_recommendation(book) -> BookRecommendation:
    """Create BookRecommendation object with safe string handling"""
    return BookRecommendation(
        product_id=safe_string_value(book.get('product_id', '')),
        title=safe_string_value(book.get('title', '')),
        authors=safe_string_value(book.get('authors', '')),
        category=safe_string_value(book.get('category', '')),
        summary=safe_string_value(book.get('summary', '')),
        personality_match_score=float(book.get('personality_match_score', 0.0)),
        cover_link=safe_string_value(book.get('cover_link', ''))
    )

def get_field_description(field: str) -> str:
    """Lấy mô tả chi tiết về lĩnh vực chuyên ngành"""
    descriptions = {
        'business': 'Kinh tế - Quản trị - Tài chính: Lĩnh vực kinh doanh, quản lý và tài chính',
        'humanities': 'Xã hội - Nhân văn: Khoa học xã hội, văn học, lịch sử, triết học',
        'science': 'Khoa học tự nhiên: Toán, lý, hóa, sinh, địa lý',
        'technology': 'Công nghệ - Kỹ thuật: IT, kỹ thuật, công nghệ thông tin',
        'medical': 'Y - Dược học: Y khoa, dược phẩm, sức khỏe',
        'education': 'Sư phạm - Giáo dục: Giảng dạy, đào tạo, phát triển con người',
        'arts': 'Nghệ thuật - Thiết kế - Kiến trúc: Sáng tạo, thiết kế, nghệ thuật',
        'agriculture': 'Nông - Lâm - Ngư nghiệp: Nông nghiệp, lâm nghiệp, thủy sản'
    }
    return descriptions.get(field, 'Lĩnh vực không xác định')

def get_learning_recommendations(motivation: str, style: str, presentation: str) -> Dict[str, str]:
    """Lấy gợi ý học tập dựa trên motivation, style và presentation"""
    recommendations = {
        'motivation_advice': {
            'foundational': 'Nên đọc sách có hệ thống, từ cơ bản đến nâng cao, có cấu trúc rõ ràng',
            'practical': 'Ưu tiên sách hướng dẫn thực hành, case study, cẩm nang ứng dụng',
            'exploratory': 'Thích hợp với sách phản biện, góc nhìn đổi mới, tư duy đột phá'
        },
        'style_advice': {
            'structured': 'Phù hợp với giáo trình, sách có lộ trình học tập từng bước',
            'integrative': 'Nên đọc sách liên ngành, tổng hợp, có tính kết nối cao'
        },
        'presentation_advice': {
            'analytical': 'Ưa thích sách chuyên sâu, có trích dẫn, nghiên cứu khoa học',
            'narrative': 'Thích sách kể chuyện, ví dụ thực tế, dễ hiểu',
            'integrative': 'Phù hợp với sách đa ngành, tư duy hệ thống'
        }
    }
    
    return {
        'motivation_tip': recommendations['motivation_advice'].get(motivation, ''),
        'style_tip': recommendations['style_advice'].get(style, ''),
        'presentation_tip': recommendations['presentation_advice'].get(presentation, '')
    }

def get_professional_book_suggestions(field: str, motivation: str, style: str, presentation: str) -> List[str]:
    """Lấy gợi ý sách dựa trên thông tin chuyên ngành"""
    suggestions = []
    
    # Gợi ý dựa trên field
    field_books = {
        'business': ['Sách kinh tế', 'Sách quản trị', 'Sách tài chính', 'Case study kinh doanh'],
        'humanities': ['Sách văn học', 'Sách lịch sử', 'Sách triết học', 'Sách xã hội học'],
        'science': ['Sách khoa học phổ thông', 'Giáo trình khoa học', 'Nghiên cứu khoa học'],
        'technology': ['Sách công nghệ', 'Sách lập trình', 'Sách kỹ thuật', 'Tài liệu IT'],
        'medical': ['Sách y khoa', 'Sách dược', 'Sách sức khỏe', 'Nghiên cứu y học'],
        'education': ['Sách giáo dục', 'Sách sư phạm', 'Phương pháp giảng dạy'],
        'arts': ['Sách nghệ thuật', 'Sách thiết kế', 'Sách kiến trúc', 'Lý thuyết nghệ thuật'],
        'agriculture': ['Sách nông nghiệp', 'Sách lâm nghiệp', 'Sách thủy sản']
    }
    
    suggestions.extend(field_books.get(field, ['Sách chuyên ngành']))
    
    # Gợi ý dựa trên motivation
    if motivation == 'foundational':
        suggestions.extend(['Sách giáo trình', 'Sách cơ bản'])
    elif motivation == 'practical':
        suggestions.extend(['Sách thực hành', 'Cẩm nang ứng dụng'])
    elif motivation == 'exploratory':
        suggestions.extend(['Sách đổi mới', 'Sách phản biện'])
    
    return list(set(suggestions))  # Loại bỏ duplicate

def map_professional_to_personality_group(field: str, motivation: str, style: str, presentation: str) -> str:
    """Map từ professional answers sang personality group phù hợp"""
    # Logic mapping dựa trên đặc điểm của từng group
    
    # Business thường là Chinh phục hoặc Kiến tạo
    if field == 'business':
        if motivation == 'exploratory':
            return 'Chinh phục'  # Khám phá cơ hội, thách thức
        else:
            return 'Kiến tạo'    # Xây dựng, phát triển
    
    # Technology/Science thường là Tri thức hoặc Kiến tạo
    elif field in ['technology', 'science']:
        if motivation == 'foundational':
            return 'Tri thức'    # Tìm hiểu bản chất
        else:
            return 'Kiến tạo'    # Ứng dụng thực tế
    
    # Humanities thường là Kết nối hoặc Tri thức
    elif field == 'humanities':
        if style == 'integrative':
            return 'Kết nối'     # Liên kết con người, xã hội
        else:
            return 'Tri thức'    # Tìm hiểu sâu sắc
    
    # Arts thường là Tự do hoặc Kết nối
    elif field == 'arts':
        if presentation == 'narrative':
            return 'Kết nối'     # Kể chuyện, cảm xúc
        else:
            return 'Tự do'       # Sáng tạo, thể hiện cá tính
    
    # Education thường là Kết nối
    elif field == 'education':
        return 'Kết nối'         # Giáo dục là kết nối con người
    
    # Medical thường là Kết nối hoặc Tri thức
    elif field == 'medical':
        if motivation == 'practical':
            return 'Kết nối'     # Chăm sóc con người
        else:
            return 'Tri thức'    # Nghiên cứu y học
    
    # Agriculture thường là Kiến tạo
    elif field == 'agriculture':
        return 'Kiến tạo'        # Xây dựng, sản xuất
    
    # Default fallback
    return 'Tri thức'

def get_personality_keywords_for_matching(primary_group: str, is_synthesizer: bool) -> List[str]:
    """Lấy keywords để match sách theo personality group"""
    base_keywords = {
        'Kết nối': [
            # Tâm lý - cảm xúc
            'tâm lý', 'cảm xúc', 'tình yêu', 'gia đình', 'mối quan hệ', 'kết nối', 'giao tiếp',
            'đồng cảm', 'chia sẻ', 'yêu thương', 'chăm sóc', 'hỗ trợ', 'giúp đỡ',
            # Văn học cảm xúc
            'tiểu thuyết', 'tản văn', 'hồi ký', 'nhật ký', 'thư từ', 'truyện ngắn',
            'văn học', 'tình cảm', 'lãng mạn', 'gia đình', 'tuổi thơ', 'kỷ niệm',
            # Phát triển bản thân - mối quan hệ
            'phát triển bản thân', 'kỹ năng mềm', 'lãnh đạo', 'teamwork', 'hợp tác',
            'xây dựng', 'nuôi dưỡng', 'giáo dục', 'con trẻ', 'parenting'
        ],
        'Tự do': [
            # Du lịch - khám phá
            'du lịch', 'khám phá', 'phiêu lưu', 'xê dịch', 'văn hóa', 'thế giới',
            'tự do', 'độc lập', 'cá nhân', 'bản sắc', 'cá tính', 'phong cách',
            # Nghệ thuật - sáng tạo  
            'nghệ thuật', 'sáng tạo', 'thiết kế', 'hội họa', 'nhiếp ảnh', 'âm nhạc',
            'thời trang', 'làm đẹp', 'phong cách sống', 'lifestyle', 'trang trí',
            # Tư duy độc lập
            'tư duy', 'suy nghĩ', 'quan điểm', 'góc nhìn', 'phản biện', 'độc đáo',
            'khác biệt', 'đổi mới', 'sáng kiến', 'breakthrough', 'innovation'
        ],
        'Tri thức': [
            # Khoa học - nghiên cứu
            'khoa học', 'nghiên cứu', 'lý thuyết', 'phương pháp', 'phân tích', 'logic',
            'toán học', 'vật lý', 'hóa học', 'sinh học', 'địa lý', 'thiên văn',
            'công nghệ', 'kỹ thuật', 'máy tính', 'lập trình', 'ai', 'robotics',
            # Lịch sử - triết học
            'lịch sử', 'triết học', 'tôn giáo', 'văn minh', 'nhân loại', 'xã hội',
            'chính trị', 'kinh tế học', 'tâm lý học', 'xã hội học', 'nhân học',
            # Học thuật
            'giáo trình', 'học thuật', 'nghiên cứu', 'luận văn', 'bài báo', 'chuyên ngành',
            'đại học', 'cao học', 'tiến sĩ', 'giáo sư', 'chuyên gia', 'expert'
        ],
        'Chinh phục': [
            # Thành công - lãnh đạo
            'thành công', 'chiến thắng', 'đạt được', 'mục tiêu', 'kết quả', 'hiệu quả',
            'lãnh đạo', 'quản lý', 'điều hành', 'chỉ đạo', 'dẫn dắt', 'leadership',
            'CEO', 'giám đốc', 'sếp', 'quản lý', 'teamlead', 'manager',
            # Thách thức - cạnh tranh
            'thách thức', 'cạnh tranh', 'đối đầu', 'vượt qua', 'chinh phục', 'đột phá',
            'chiến lược', 'tactic', 'kế hoạch', 'planning', 'strategy', 'execution',
            # Truyền cảm hứng
            'truyền cảm hứng', 'động lực', 'motivation', 'inspiring', 'passionate',
            'quyết tâm', 'ý chí', 'bền bỉ', 'kiên trì', 'vượt khó', 'overcome'
        ],
        'Kiến tạo': [
            # Kinh doanh - khởi nghiệp
            'kinh doanh', 'khởi nghiệp', 'startup', 'doanh nghiệp', 'công ty', 'business',
            'marketing', 'bán hàng', 'sales', 'customer', 'khách hàng', 'thị trường',
            'đầu tư', 'tài chính', 'ngân hàng', 'chứng khoán', 'real estate', 'bất động sản',
            # Kỹ năng thực tế
            'kỹ năng', 'thực hành', 'ứng dụng', 'practical', 'hands-on', 'tutorial',
            'hướng dẫn', 'cẩm nang', 'manual', 'guide', 'how-to', 'step-by-step',
            # Xây dựng - phát triển
            'xây dựng', 'phát triển', 'tăng trưởng', 'growth', 'scale', 'expansion',
            'hệ thống', 'quy trình', 'process', 'system', 'framework', 'methodology'
        ]
    }
    
    keywords = base_keywords.get(primary_group, [])
    
    # Nếu là synthesizer, thêm keywords liên ngành
    if is_synthesizer:
        synthesizer_keywords = [
            'liên ngành', 'đa ngành', 'tổng hợp', 'kết hợp', 'tích hợp', 'interdisciplinary',
            'multidisciplinary', 'cross-functional', 'holistic', 'comprehensive',
            'tư duy hệ thống', 'systems thinking', 'big picture', 'toàn cảnh',
            'liên kết', 'kết nối', 'integration', 'synthesis', 'convergence'
        ]
        keywords.extend(synthesizer_keywords)
    
    return keywords

def create_book_list_item(book_row) -> BookListItem:
    """Create BookListItem object with safe string handling (without content)"""
    return BookListItem(
        product_id=safe_string_value(book_row.get('product_id', '')),
        title=safe_string_value(book_row.get('title', '')),
        authors=safe_string_value(book_row.get('authors', '')),
        original_price=float(book_row.get('original_price', 0)) if pd.notna(book_row.get('original_price')) else None,
        current_price=float(book_row.get('current_price', 0)) if pd.notna(book_row.get('current_price')) else None,
        category=safe_string_value(book_row.get('category', '')),
        n_review=int(book_row.get('n_review', 0)) if pd.notna(book_row.get('n_review')) else None,
        avg_rating=float(book_row.get('avg_rating', 0)) if pd.notna(book_row.get('avg_rating')) else None,
        pages=int(book_row.get('pages', 0)) if pd.notna(book_row.get('pages')) else None,
        manufacturer=safe_string_value(book_row.get('manufacturer', '')),
        cover_link=safe_string_value(book_row.get('cover_link', '')),
        summary=safe_string_value(book_row.get('summary', ''))
    )

def create_book_detail(book_row) -> BookDetail:
    """Create BookDetail object with safe string handling (with full content)"""
    return BookDetail(
        product_id=safe_string_value(book_row.get('product_id', '')),
        title=safe_string_value(book_row.get('title', '')),
        authors=safe_string_value(book_row.get('authors', '')),
        original_price=float(book_row.get('original_price', 0)) if pd.notna(book_row.get('original_price')) else None,
        current_price=float(book_row.get('current_price', 0)) if pd.notna(book_row.get('current_price')) else None,
        quantity=float(book_row.get('quantity', 0)) if pd.notna(book_row.get('quantity')) else None,
        category=safe_string_value(book_row.get('category', '')),
        n_review=int(book_row.get('n_review', 0)) if pd.notna(book_row.get('n_review')) else None,
        avg_rating=float(book_row.get('avg_rating', 0)) if pd.notna(book_row.get('avg_rating')) else None,
        pages=int(book_row.get('pages', 0)) if pd.notna(book_row.get('pages')) else None,
        manufacturer=safe_string_value(book_row.get('manufacturer', '')),
        cover_link=safe_string_value(book_row.get('cover_link', '')),
        summary=safe_string_value(book_row.get('summary', '')),
        content=' '.join(safe_string_value(book_row.get('content', '')).split()[:100])
    )

def load_book_database():
    """Load book database with fallback options"""
    book_file = 'dataset/books_full_data.csv'
    if not os.path.exists(book_file):
        fallback_files = [
            'books_full_data.csv',
            '../dataset/books_full_data.csv',
            'v2/labeled_books_v2.csv'
        ]
        
        for file_path in fallback_files:
            if os.path.exists(file_path):
                book_file = file_path
                break
        
        if not os.path.exists(book_file):
            raise HTTPException(status_code=404, detail="Book database not found")
    
    return pd.read_csv(book_file)


def ensure_complete_discovery_answers(answers: Dict[str, str]) -> Dict[str, str]:
    """Ensure answers dict contains Q1..Q8 by filling missing with a safe default (first available choice).

    This prevents the recommender from receiving an incomplete answers set when only Q1-Q3 are provided.
    """
    complete = answers.copy()
    for q in [f'Q{i}' for i in range(1, 9)]:
        if q not in complete or complete[q] is None:
            # pick the first available choice key for that question
            try:
                choices = personality_system.discovery_questions[q]['choices']
                if isinstance(choices, dict) and len(choices) > 0:
                    first_choice = next(iter(choices.keys()))
                    complete[q] = first_choice
                else:
                    complete[q] = 'A'
            except Exception:
                complete[q] = 'A'
    return complete

def get_personality_description(primary_group: str, is_synthesizer: bool) -> Dict[str, str]:
    """Lấy mô tả chi tiết về nhóm tính cách"""
    descriptions = {
        'Kết nối': {
            'title': '🤝 The Connectors - Người Kết nối',
            'description': 'Bạn đọc sách để tìm kiếm sự hòa hợp, tình yêu và cảm giác thuộc về. Bạn thích những câu chuyện chạm đến trái tim, giúp bạn hiểu và đồng cảm với người khác.',
            'books': 'Tâm lý tình cảm, chữa lành, tản văn, tiểu thuyết gia đình',
            'traits': 'Đồng cảm cao, thích kết nối, ưa câu chuyện cảm động'
        },
        'Tự do': {
            'title': '🕊️ The Individuals - Người Tự do', 
            'description': 'Bạn tìm kiếm tự do, thể hiện bản sắc cá nhân và phá vỡ khuôn mẫu. Đọc sách là cách bạn khám phá thế giới và định hình cá tính riêng.',
            'books': 'Du ký, nghệ thuật sống, tiểu thuyết sáng tạo, sách phản tư xã hội',
            'traits': 'Độc lập, sáng tạo, thích khám phá bản thân'
        },
        'Tri thức': {
            'title': '🧠 The Thinkers - Người Tư duy',
            'description': 'Bạn tìm kiếm tri thức, sự thật và lý giải thế giới. Mỗi cuốn sách là một câu hỏi cần được trả lời, một bí ẩn cần được khám phá.',
            'books': 'Khoa học phổ thông, triết học, lịch sử, sách phân tích chuyên sâu',
            'traits': 'Hiếu học, logic, thích phân tích và tìm hiểu'
        },
        'Chinh phục': {
            'title': '🏆 The Achievers - Người Chinh phục',
            'description': 'Bạn muốn vượt qua thử thách, tạo ra thành tựu và biến ý tưởng thành hiện thực. Sách là công cụ giúp bạn đạt được mục tiêu.',
            'books': 'Sách truyền cảm hứng, lãnh đạo, chiến lược, hồi ký thành công',
            'traits': 'Quyết đoán, hướng mục tiêu, thích thách thức'
        },
        'Kiến tạo': {
            'title': '🏗️ The Builders - Người Xây dựng',
            'description': 'Bạn muốn xây dựng nền tảng vững chắc, phát triển kỹ năng thực tế. Bạn thích những cuốn sách có tính ứng dụng cao.',
            'books': 'Sách kỹ năng, tài chính, marketing, khởi nghiệp, sách hướng nghiệp',
            'traits': 'Thực tế, có hệ thống, thích xây dựng và phát triển'
        }
    }
    
    desc = descriptions[primary_group].copy()
    
    if is_synthesizer:
        desc['synthesizer_note'] = (
            "🔗 Đặc điểm Synthesizer: Bạn có khả năng tư duy tổng hợp cao, "
            "thích kết nối tri thức từ nhiều lĩnh vực khác nhau. Phù hợp với "
            "sách có chiều sâu và khả năng liên kết đa ngành."
        )
    
    return desc

# === API ENDPOINTS ===

@app.get("/")
async def root():
    """Endpoint gốc"""
    return {
        "message": "Caelio Personality API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/questions", response_model=Dict[str, QuestionData])
async def get_questions(question_type: str = "discovery"):
    """Lấy tất cả câu hỏi cho personality test
    
    Args:
        question_type: 'discovery' cho hành trình khám phá, 'professional' cho hành trình chuyên ngành
    """
    if question_type == "discovery":
        source_questions = personality_system.discovery_questions
    elif question_type == "professional":
        source_questions = personality_system.professional_questions
    else:
        raise HTTPException(status_code=400, detail="question_type must be 'discovery' or 'professional'")
    
    questions = {}
    for q_id, question_data in source_questions.items():
        # Handle different choice formats between discovery and professional questions
        choices_formatted = {}
        for choice_id, choice_data in question_data['choices'].items():
            if question_type == "discovery":
                choices_formatted[choice_id] = {
                    'text': choice_data['text'],
                    'group': choice_data.get('group', ''),
                    'synthesizer': choice_data.get('synthesizer', False)
                }
            else:  # professional
                choices_formatted[choice_id] = {
                    'text': choice_data['text'],
                    'field': choice_data.get('field', ''),
                    'motivation': choice_data.get('motivation', ''),
                    'style': choice_data.get('style', ''),
                    'presentation': choice_data.get('presentation', ''),
                    'synthesizer_potential': choice_data.get('synthesizer_potential', False),
                    'synthesizer': choice_data.get('synthesizer', False)
                }
        
        questions[q_id] = QuestionData(
            question=question_data['question'],
            choices=choices_formatted
        )
    
    return questions

@app.get("/questions/{question_id}")
async def get_question(question_id: str, question_type: str = "discovery"):
    """Lấy câu hỏi cụ thể
    
    Args:
        question_id: ID của câu hỏi (Q1, Q2, ...)
        question_type: 'discovery' hoặc 'professional'
    """
    if question_type == "discovery":
        source_questions = personality_system.discovery_questions
    elif question_type == "professional":
        source_questions = personality_system.professional_questions
    else:
        raise HTTPException(status_code=400, detail="question_type must be 'discovery' or 'professional'")
    
    if question_id not in source_questions:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question_data = source_questions[question_id]
    
    # Format choices based on question type
    choices_formatted = {}
    for choice_id, choice_data in question_data['choices'].items():
        if question_type == "discovery":
            choices_formatted[choice_id] = {
                'text': choice_data['text'],
                'group': choice_data.get('group', ''),
                'synthesizer': choice_data.get('synthesizer', False)
            }
        else:  # professional
            choices_formatted[choice_id] = {
                'text': choice_data['text'],
                'field': choice_data.get('field', ''),
                'motivation': choice_data.get('motivation', ''),
                'style': choice_data.get('style', ''),
                'presentation': choice_data.get('presentation', ''),
                'synthesizer_potential': choice_data.get('synthesizer_potential', False),
                'synthesizer': choice_data.get('synthesizer', False)
            }
    
    return QuestionData(
        question=question_data['question'],
        choices=choices_formatted
    )

@app.post("/analyze", response_model=PersonalityProfile)
async def analyze_personality(answers: PersonalityAnswers):
    """Phân tích tính cách từ câu trả lời hành trình khám phá (3 hoặc 8 câu)"""
    try:
        # Chuyển đổi sang format dictionary và loại bỏ None values
        answers_dict = {k: v for k, v in answers.dict().items() if v is not None}
        
        # Kiểm tra số lượng câu trả lời (phải là 3 hoặc 8)
        num_answers = len(answers_dict)
        if num_answers != 3 and num_answers != 8:
            raise HTTPException(status_code=400, detail="Must provide either 3 answers (Q1-Q3) or 8 answers (Q1-Q8)")
        
        # Validate answers
        for q_id, answer in answers_dict.items():
            if q_id not in personality_system.discovery_questions:
                raise HTTPException(status_code=400, detail=f"Invalid question ID: {q_id}")
            
            question_choices = personality_system.discovery_questions[q_id]['choices']
            if answer not in question_choices:
                raise HTTPException(status_code=400, detail=f"Invalid answer '{answer}' for question {q_id}")
        
        # Phân tích dựa trên số câu trả lời
        if num_answers == 3:
            # Phân tích sơ bộ từ 3 câu đầu (WHY questions)
            profile = personality_system.calculate_partial_profile(answers_dict)
        else:
            # Phân tích đầy đủ từ 8 câu
            profile = personality_system.calculate_discovery_profile(answers_dict)
        
        # Lấy mô tả
        description = get_personality_description(profile['primary_group'], profile['is_synthesizer'])
        
        return PersonalityProfile(
            primary_group=profile['primary_group'],
            secondary_group=profile['secondary_group'],
            primary_score=profile['primary_score'],
            secondary_score=profile['secondary_score'],
            synthesizer_score=profile['synthesizer_score'],
            is_synthesizer=profile['is_synthesizer'],
            profile_name=profile['profile_name'],
            english_name=profile['english_name'],
            all_scores=profile['all_scores'],
            is_multi_motivated=profile['is_multi_motivated'],
            description=description
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing personality: {str(e)}")

@app.post("/analyze-professional", response_model=Dict[str, Any])
async def analyze_professional_personality(answers: ProfessionalAnswers):
    """Phân tích chuyên ngành từ 4 câu hỏi chuyên ngành (Q1-Q4)"""
    try:
        # Chuyển đổi sang format dictionary
        professional_dict = answers.dict()
        
        # Validate professional answers
        for q_id, answer in professional_dict.items():
            if q_id not in personality_system.professional_questions:
                raise HTTPException(status_code=400, detail=f"Invalid professional question ID: {q_id}")
            
            question_choices = personality_system.professional_questions[q_id]['choices']
            if answer not in question_choices:
                raise HTTPException(status_code=400, detail=f"Invalid answer '{answer}' for professional question {q_id}")
        
        # Phân tích thông tin chuyên ngành
        field = personality_system.professional_questions['Q1']['choices'][professional_dict['Q1']]['field']
        motivation = personality_system.professional_questions['Q2']['choices'][professional_dict['Q2']]['motivation'] 
        style = personality_system.professional_questions['Q3']['choices'][professional_dict['Q3']]['style']
        presentation = personality_system.professional_questions['Q4']['choices'][professional_dict['Q4']]['presentation']
        
        # Kiểm tra Synthesizer tiềm năng trong chuyên ngành
        synthesizer_indicators = 0
        if professional_dict['Q3'] == 'B':  # Tự mình tìm liên kết
            synthesizer_indicators += 1
        if professional_dict['Q4'] == 'C':  # Kết nối đa ngành
            synthesizer_indicators += 1
        
        return {
            'field': field,
            'motivation': motivation,
            'learning_style': style,
            'presentation_preference': presentation,
            'professional_synthesizer_indicators': synthesizer_indicators,
            'is_professional_synthesizer': synthesizer_indicators >= 2,
            'field_description': get_field_description(field),
            'learning_recommendations': get_learning_recommendations(motivation, style, presentation)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing professional profile: {str(e)}")

@app.post("/recommend", response_model=RecommendationResult)
async def get_book_recommendations(answers: PersonalityAnswers, top_n: int = 20):
    """Lấy gợi ý sách dựa trên personality profile"""
    try:
        # Phân tích tính cách
        answers_dict = answers.dict()
        profile = personality_system.calculate_discovery_profile(answers_dict)
        
        # Thêm description
        description = get_personality_description(profile['primary_group'], profile['is_synthesizer'])
        
        # Load dữ liệu sách
        book_df = load_book_database()
        
        # Lấy gợi ý sách với improved matching (same as /discover)
        personality_keywords = get_personality_keywords_for_matching(profile['primary_group'], profile['is_synthesizer'])
        
        # Score và filter sách
        scored_books = []
        for _, book in book_df.iterrows():
            cat = safe_string_value(book.get('category', '')).lower()
            title = safe_string_value(book.get('title', '')).lower() 
            summary = safe_string_value(book.get('summary', '')).lower()
            content = safe_string_value(book.get('content', '')).lower()
            
            # Calculate match score
            match_score = 0.0
            total_keywords = len(personality_keywords)
            
            for keyword in personality_keywords:
                keyword_score = 0
                if keyword in cat:
                    keyword_score += 3
                if keyword in title:
                    keyword_score += 2
                if keyword in summary:
                    keyword_score += 1
                if keyword in content:
                    keyword_score += 0.5
                
                if keyword_score > 0:
                    match_score += keyword_score / total_keywords
            
            # Sales and quality bonuses
            quantity = float(book.get('quantity', 0)) if pd.notna(book.get('quantity')) else 0
            sales_boost = min(quantity / 10000, 1.0) * 0.2
            
            avg_rating = float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else 0
            n_review = int(book.get('n_review', 0)) if pd.notna(book.get('n_review')) else 0
            
            rating_boost = (avg_rating / 5.0) * 0.1 if avg_rating > 0 else 0
            review_boost = min(n_review / 1000, 1.0) * 0.1 if n_review > 0 else 0
            
            final_score = match_score + sales_boost + rating_boost + review_boost
            
            if final_score > 0.05:
                scored_books.append((book, final_score))
        
        # Sort by score and sales
        scored_books.sort(key=lambda x: (x[1], float(x[0].get('quantity', 0)) if pd.notna(x[0].get('quantity')) else 0), reverse=True)
        
        # Create recommendations
        recommendations = []
        match_distribution = {}
        
        for book, score in scored_books[:top_n]:
            book_rec = create_book_recommendation(book)
            book_rec.personality_match_score = score
            recommendations.append(book_rec)
            
            category = safe_string_value(book.get('category', 'Unknown'))
            match_distribution[category] = match_distribution.get(category, 0) + 1
        
        # Tạo profile response
        profile_response = PersonalityProfile(
            primary_group=profile['primary_group'],
            secondary_group=profile['secondary_group'],
            primary_score=profile['primary_score'],
            secondary_score=profile['secondary_score'],
            synthesizer_score=profile['synthesizer_score'],
            is_synthesizer=profile['is_synthesizer'],
            profile_name=profile['profile_name'],
            english_name=profile['english_name'],
            all_scores=profile['all_scores'],
            is_multi_motivated=profile['is_multi_motivated'],
            description=description
        )
        
        return RecommendationResult(
            profile=profile_response,
            recommendations=recommendations,
            total_matches=len(scored_books),
            match_distribution=match_distribution
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.post("/recommend-professional", response_model=Dict[str, Any])
async def get_professional_book_recommendations(answers: ProfessionalAnswers, top_n: int = 20):
    """Lấy gợi ý sách dựa trên thông tin chuyên ngành (4 câu hỏi)"""
    try:
        # Phân tích thông tin chuyên ngành
        professional_dict = answers.dict()
        
        # Validate professional answers
        for q_id, answer in professional_dict.items():
            if q_id not in personality_system.professional_questions:
                raise HTTPException(status_code=400, detail=f"Invalid professional question ID: {q_id}")
            
            question_choices = personality_system.professional_questions[q_id]['choices']
            if answer not in question_choices:
                raise HTTPException(status_code=400, detail=f"Invalid answer '{answer}' for professional question {q_id}")
        
        # Phân tích thông tin chuyên ngành
        field = personality_system.professional_questions['Q1']['choices'][professional_dict['Q1']]['field']
        motivation = personality_system.professional_questions['Q2']['choices'][professional_dict['Q2']]['motivation'] 
        style = personality_system.professional_questions['Q3']['choices'][professional_dict['Q3']]['style']
        presentation = personality_system.professional_questions['Q4']['choices'][professional_dict['Q4']]['presentation']
        
        synthesizer_indicators = 0
        if professional_dict['Q3'] == 'B':
            synthesizer_indicators += 1
        if professional_dict['Q4'] == 'C':
            synthesizer_indicators += 1
        
        # Gợi ý sách dựa trên field và motivation (đơn giản)
        book_recommendations = get_professional_book_suggestions(field, motivation, style, presentation)
        
        return {
            'professional_analysis': {
                'field': field,
                'motivation': motivation,
                'learning_style': style,
                'presentation_preference': presentation,
                'professional_synthesizer_indicators': synthesizer_indicators,
                'is_professional_synthesizer': synthesizer_indicators >= 2,
                'field_description': get_field_description(field),
                'learning_recommendations': get_learning_recommendations(motivation, style, presentation)
            },
            'book_suggestions': book_recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting professional recommendations: {str(e)}")

@app.post("/discover", response_model=RecommendationResult)
async def discover_and_recommend(answers: PersonalityAnswers, top_n: int = 20):
    """API tổng hợp: Phân tích tính cách + Gợi ý sách cho hành trình khám phá"""
    try:
        # Chuyển đổi sang format dictionary và loại bỏ None values
        answers_dict = {k: v for k, v in answers.dict().items() if v is not None}
        
        # Kiểm tra số lượng câu trả lời (phải là 3 hoặc 8)
        num_answers = len(answers_dict)
        if num_answers != 3 and num_answers != 8:
            raise HTTPException(status_code=400, detail="Must provide either 3 answers (Q1-Q3) or 8 answers (Q1-Q8)")
        
        # Validate answers
        for q_id, answer in answers_dict.items():
            if q_id not in personality_system.discovery_questions:
                raise HTTPException(status_code=400, detail=f"Invalid question ID: {q_id}")
            
            question_choices = personality_system.discovery_questions[q_id]['choices']
            if answer not in question_choices:
                raise HTTPException(status_code=400, detail=f"Invalid answer '{answer}' for question {q_id}")
        
        # Phân tích dựa trên số câu trả lời
        if num_answers == 3:
            # Phân tích sơ bộ từ 3 câu đầu (WHY questions)
            profile = personality_system.calculate_partial_profile(answers_dict)
        else:
            # Phân tích đầy đủ từ 8 câu
            profile = personality_system.calculate_discovery_profile(answers_dict)
        
        # Lấy mô tả
        description = get_personality_description(profile['primary_group'], profile['is_synthesizer'])
        
        # Load dữ liệu sách
        book_df = load_book_database()
        
        # Lấy gợi ý sách với improved matching
        # Get keywords for personality matching
        personality_keywords = get_personality_keywords_for_matching(profile['primary_group'], profile['is_synthesizer'])
        
        # Score và filter sách
        scored_books = []
        for _, book in book_df.iterrows():
            cat = safe_string_value(book.get('category', '')).lower()
            title = safe_string_value(book.get('title', '')).lower() 
            summary = safe_string_value(book.get('summary', '')).lower()
            content = safe_string_value(book.get('content', '')).lower()
            
            # Calculate match score based on keywords
            match_score = 0.0
            total_keywords = len(personality_keywords)
            
            for keyword in personality_keywords:
                keyword_score = 0
                if keyword in cat:
                    keyword_score += 3  # Category match is most important
                if keyword in title:
                    keyword_score += 2  # Title match is very important
                if keyword in summary:
                    keyword_score += 1  # Summary match is important
                if keyword in content:
                    keyword_score += 0.5  # Content match is less important
                
                if keyword_score > 0:
                    match_score += keyword_score / total_keywords
            
            # Bonus for sales volume (quantity)
            quantity = float(book.get('quantity', 0)) if pd.notna(book.get('quantity')) else 0
            sales_boost = min(quantity / 10000, 1.0) * 0.2  # Max 20% boost for high sales
            
            # Bonus for rating and reviews
            avg_rating = float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else 0
            n_review = int(book.get('n_review', 0)) if pd.notna(book.get('n_review')) else 0
            
            rating_boost = (avg_rating / 5.0) * 0.1 if avg_rating > 0 else 0  # Max 10% boost for high rating
            review_boost = min(n_review / 1000, 1.0) * 0.1 if n_review > 0 else 0  # Max 10% boost for many reviews
            
            final_score = match_score + sales_boost + rating_boost + review_boost
            
            if final_score > 0.05:  # Threshold for inclusion
                scored_books.append((book, final_score))
        
        # Sort by score (descending) and sales volume (descending)
        scored_books.sort(key=lambda x: (x[1], float(x[0].get('quantity', 0)) if pd.notna(x[0].get('quantity')) else 0), reverse=True)
        
        # Take top_n recommendations
        recommendations = []
        match_distribution = {}
        
        for book, score in scored_books[:top_n]:
            book_rec = create_book_recommendation(book)
            book_rec.personality_match_score = score
            recommendations.append(book_rec)
            
            # Track distribution
            category = safe_string_value(book.get('category', 'Unknown'))
            match_distribution[category] = match_distribution.get(category, 0) + 1
        
        # Tạo profile response
        profile_response = PersonalityProfile(
            primary_group=profile['primary_group'],
            secondary_group=profile['secondary_group'],
            primary_score=profile['primary_score'],
            secondary_score=profile['secondary_score'],
            synthesizer_score=profile['synthesizer_score'],
            is_synthesizer=profile['is_synthesizer'],
            profile_name=profile['profile_name'],
            english_name=profile['english_name'],
            all_scores=profile['all_scores'],
            is_multi_motivated=profile['is_multi_motivated'],
            description=description
        )
        
        return RecommendationResult(
            profile=profile_response,
            recommendations=recommendations,
            total_matches=len(scored_books),
            match_distribution=match_distribution
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in discover and recommend: {str(e)}")

@app.post("/professional", response_model=RecommendationResult)
async def professional_and_recommend(answers: ProfessionalAnswers, top_n: int = 20):
    """API tổng hợp chuyên ngành: Phân tích + Gợi ý sách từ 4 câu hỏi chuyên ngành"""
    try:
        # Phân tích thông tin chuyên ngành
        professional_dict = answers.dict()
        
        # Validate professional answers
        for q_id, answer in professional_dict.items():
            if q_id not in personality_system.professional_questions:
                raise HTTPException(status_code=400, detail=f"Invalid professional question ID: {q_id}")
            
            question_choices = personality_system.professional_questions[q_id]['choices']
            if answer not in question_choices:
                raise HTTPException(status_code=400, detail=f"Invalid answer '{answer}' for professional question {q_id}")
        
        # Phân tích thông tin chuyên ngành
        field = personality_system.professional_questions['Q1']['choices'][professional_dict['Q1']]['field']
        motivation = personality_system.professional_questions['Q2']['choices'][professional_dict['Q2']]['motivation'] 
        style = personality_system.professional_questions['Q3']['choices'][professional_dict['Q3']]['style']
        presentation = personality_system.professional_questions['Q4']['choices'][professional_dict['Q4']]['presentation']
        
        # Kiểm tra Synthesizer tiềm năng
        synthesizer_indicators = 0
        if professional_dict['Q3'] == 'B':  # Tự mình tìm liên kết
            synthesizer_indicators += 1
        if professional_dict['Q4'] == 'C':  # Kết nối đa ngành
            synthesizer_indicators += 1
        
        is_synthesizer = synthesizer_indicators >= 2
        
        # Map professional answers sang personality group hợp lý
        primary_group = map_professional_to_personality_group(field, motivation, style, presentation)
        
        # Tạo personality profile từ professional context
        profile = {
            'primary_group': primary_group,
            'secondary_group': None,
            'primary_score': 100,  # Professional context gives strong indication
            'secondary_score': 0,
            'synthesizer_score': synthesizer_indicators * 50,
            'is_synthesizer': is_synthesizer,
            'profile_name': f"{primary_group}{'–Synthesizer' if is_synthesizer else ''}",
            'english_name': f"Professional {primary_group}{'–Synthesizer' if is_synthesizer else ''}",
            'all_scores': {primary_group: 100, 'Synthesizer': synthesizer_indicators * 50},
            'is_multi_motivated': False
        }

        # Load book database
        book_df = load_book_database()

        # Lấy keywords cho matching dựa trên personality + field
        personality_keywords = get_personality_keywords_for_matching(primary_group, is_synthesizer)
        field_keywords = {
            'business': ['kinh doanh', 'marketing', 'bán hàng', 'quản trị', 'tài chính', 'kế toán', 'chứng khoán', 'đầu tư', 'khởi nghiệp'],
            'humanities': ['văn học', 'lịch sử', 'triết học', 'xã hội', 'nhân văn', 'tôn giáo', 'văn hóa'],
            'science': ['khoa học', 'toán học', 'vật lý', 'hóa học', 'sinh học', 'địa lý', 'kỹ thuật'],
            'technology': ['công nghệ', 'tin học', 'lập trình', 'máy tính', 'internet', 'ai', 'robot'],
            'medical': ['y học', 'sức khỏe', 'dược', 'y khoa', 'chăm sóc', 'dinh dưỡng'],
            'education': ['giáo dục', 'sư phạm', 'dạy học', 'đào tạo', 'trẻ em'],
            'arts': ['nghệ thuật', 'hội họa', 'thiết kế', 'kiến trúc', 'âm nhạc', 'múa', 'thời trang'],
            'agriculture': ['nông nghiệp', 'lâm nghiệp', 'thủy sản', 'trồng trọt', 'chăn nuôi']
        }
        
        # Kết hợp keywords từ personality và field
        all_keywords = personality_keywords + field_keywords.get(field, [])
        
        # Score và filter sách
        scored_books = []
        for _, book in book_df.iterrows():
            cat = safe_string_value(book.get('category', '')).lower()
            title = safe_string_value(book.get('title', '')).lower() 
            summary = safe_string_value(book.get('summary', '')).lower()
            content = safe_string_value(book.get('content', '')).lower()
            
            # Calculate match score
            match_score = 0.0
            total_keywords = len(all_keywords)
            
            for keyword in all_keywords:
                keyword_score = 0
                if keyword in cat:
                    keyword_score += 3  # Category match is most important
                if keyword in title:
                    keyword_score += 2  # Title match is very important
                if keyword in summary:
                    keyword_score += 1  # Summary match is important
                if keyword in content:
                    keyword_score += 0.5  # Content match is less important
                
                if keyword_score > 0:
                    match_score += keyword_score / total_keywords
            
            # Bonus for sales volume (quantity)
            quantity = float(book.get('quantity', 0)) if pd.notna(book.get('quantity')) else 0
            sales_boost = min(quantity / 10000, 1.0) * 0.2  # Max 20% boost for high sales
            
            final_score = match_score + sales_boost
            
            if final_score > 0.05:  # Threshold for inclusion
                scored_books.append((book, final_score))
        
        # Sort by score (descending) and sales volume (descending)
        scored_books.sort(key=lambda x: (x[1], float(x[0].get('quantity', 0)) if pd.notna(x[0].get('quantity')) else 0), reverse=True)
        
        # Take top_n recommendations
        recommendations = []
        match_distribution = {}
        
        for book, score in scored_books[:top_n]:
            book_rec = create_book_recommendation(book)
            book_rec.personality_match_score = score
            recommendations.append(book_rec)
            
            # Track distribution
            category = safe_string_value(book.get('category', 'Unknown'))
            match_distribution[category] = match_distribution.get(category, 0) + 1

        # Tạo profile response
        description = get_personality_description(primary_group, is_synthesizer)
        profile_response = PersonalityProfile(
            primary_group=profile['primary_group'],
            secondary_group=profile['secondary_group'],
            primary_score=profile['primary_score'],
            secondary_score=profile['secondary_score'],
            synthesizer_score=profile['synthesizer_score'],
            is_synthesizer=profile['is_synthesizer'],
            profile_name=profile['profile_name'],
            english_name=profile['english_name'],
            all_scores=profile['all_scores'],
            is_multi_motivated=profile['is_multi_motivated'],
            description=description
        )

        return RecommendationResult(
            profile=profile_response,
            recommendations=recommendations,
            total_matches=len(scored_books),
            match_distribution=match_distribution
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in professional and recommend: {str(e)}")

@app.get("/books", response_model=BookListResponse)
async def get_books(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None
):
    """Lấy danh sách sách với phân trang và lọc
    
    Args:
        page: Số trang (bắt đầu từ 1)
        page_size: Số sách mỗi trang (tối đa 100)
        category: Lọc theo category (tìm kiếm tương đối)
        author: Lọc theo tác giả (tìm kiếm tương đối)
        title: Lọc theo tiêu đề (tìm kiếm tương đối)
    """
    try:
        # Validate parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
        
        # Load book database
        book_df = load_book_database()
        
        # Apply filters
        filtered_df = book_df.copy()
        
        if category:
            category_lower = category.lower()
            filtered_df = filtered_df[
                filtered_df['category'].str.lower().str.contains(category_lower, na=False, regex=False)
            ]
        
        if author:
            author_lower = author.lower()
            filtered_df = filtered_df[
                filtered_df['authors'].str.lower().str.contains(author_lower, na=False, regex=False)
            ]
        
        if title:
            title_lower = title.lower()
            filtered_df = filtered_df[
                filtered_df['title'].str.lower().str.contains(title_lower, na=False, regex=False)
            ]
        
        # Calculate pagination
        total = len(filtered_df)
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        # Get paginated results
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = filtered_df.iloc[start_idx:end_idx]
        
        # Convert to BookListItem objects
        books = []
        for _, book_row in paginated_df.iterrows():
            books.append(create_book_list_item(book_row))
        
        return BookListResponse(
            books=books,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting books: {str(e)}")

@app.get("/books/{product_id}", response_model=BookDetail)
async def get_book_detail(product_id: str):
    """Lấy thông tin chi tiết của một cuốn sách
    
    Args:
        product_id: ID sản phẩm của cuốn sách
    """
    try:
        # Load book database
        book_df = load_book_database()
        
        # Find book by product_id
        # Convert product_id to string for comparison since it might be stored as different types
        book_matches = book_df[book_df['product_id'].astype(str) == str(product_id)]
        
        if len(book_matches) == 0:
            raise HTTPException(status_code=404, detail=f"Book with product_id '{product_id}' not found")
        
        # Get the first match (should be unique)
        book_row = book_matches.iloc[0]
        
        # Convert to BookDetail object
        return create_book_detail(book_row)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book detail: {str(e)}")

@app.get("/groups")
async def get_personality_groups():
    """Lấy danh sách các nhóm tính cách"""
    return {
        "groups": personality_system.groups,
        "descriptions": {
            group: get_personality_description(group, False)
            for group in personality_system.groups.keys()
        }
    }

@app.get("/stats")
async def get_system_stats():
    """Lấy thống kê hệ thống"""
    try:
        # Đếm số câu hỏi
        num_discovery_questions = len(personality_system.discovery_questions)
        num_professional_questions = len(personality_system.professional_questions)
        
        # Đếm số sách (nếu có database)
        num_books = 0
        try:
            book_df = pd.read_csv('dataset/books_full_data.csv')
            num_books = len(book_df)
        except:
            pass
        
        return {
            "discovery_questions": num_discovery_questions,
            "professional_questions": num_professional_questions,
            "total_questions": num_discovery_questions + num_professional_questions,
            "total_personality_groups": len(personality_system.groups),
            "total_books": num_books,
            "synthesizer_available": True,
            "journey_types": ["discovery", "professional"],
            "api_version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# === DEVELOPMENT ENDPOINTS ===

@app.post("/test/example")
async def test_example():
    """Test với ví dụ từ documentation"""
    example_answers = PersonalityAnswers(
        Q1="C", Q2="D", Q3="E", Q4="C", 
        Q5="B", Q6="E", Q7="C", Q8="C"
    )
    
    result = await analyze_personality(example_answers)
    return {
        "test_case": "Documentation example",
        "expected": "Thinker–Synthesizer", 
        "actual": result.profile_name,
        "passed": "Tri thức" in result.profile_name and "Synthesizer" in result.profile_name,
        "profile": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)