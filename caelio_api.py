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
        book_file = 'dataset/books_full_data.csv'
        if not os.path.exists(book_file):
            # Fallback files
            fallback_files = [
                'books_full_data.csv',
                '../dataset/books_full_data.csv',
                'v2/labeled_books_v2.csv'
            ]
            
            book_df = None
            for file_path in fallback_files:
                if os.path.exists(file_path):
                    book_file = file_path
                    break
            
            if not os.path.exists(book_file):
                raise HTTPException(status_code=404, detail="Book database not found")
        
        book_df = pd.read_csv(book_file)
        
        # Lấy gợi ý sách
        # Ensure we pass a complete answers dict (Q1..Q8) to the matcher
        complete_answers = ensure_complete_discovery_answers(answers_dict)
        result = book_matcher.get_personalized_recommendations(complete_answers, book_df, top_n=top_n)

        # Chuyển đổi recommendations sang format API
        recommendations = []
        for _, book in result['recommendations'].iterrows():
            recommendations.append(create_book_recommendation(book))
        
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
            total_matches=result['total_matches'],
            match_distribution=result['match_distribution']
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
        
        book_df = pd.read_csv(book_file)
        
        # Lấy gợi ý sách
        # Ensure we pass a complete answers dict (Q1..Q8) to the matcher
        complete_answers = ensure_complete_discovery_answers(answers_dict)
        result = book_matcher.get_personalized_recommendations(complete_answers, book_df, top_n=top_n)

        # Chuyển đổi recommendations sang format API
        recommendations = []
        for _, book in result['recommendations'].iterrows():
            recommendations.append(create_book_recommendation(book))
        
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
            total_matches=result['total_matches'],
            match_distribution=result['match_distribution']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in discover and recommend: {str(e)}")

@app.post("/professional", response_model=Dict[str, Any])
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
        
        # Use personalized matcher with professional context
        # Convert professional answers to discovery-style answers for compatibility
        discovery_answers = {
            'Q1': professional_dict.get('Q1', 'A'),
            'Q2': professional_dict.get('Q2', 'A'), 
            'Q3': professional_dict.get('Q3', 'A'),
            'Q4': 'A',  # Default for remaining questions
            'Q5': 'A',
            'Q6': 'A', 
            'Q7': 'A',
            'Q8': 'A'
        }

        # Load book DB
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

        book_df = pd.read_csv(book_file)

        # Get basic recommendations using personality matcher
        result = book_matcher.get_personalized_recommendations(discovery_answers, book_df, top_n=top_n*2)

        # Filter by professional field with fuzzy matching
        recommendations = []
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
        
        field_words = field_keywords.get(field, [])
        
        for _, book in result['recommendations'].iterrows():
            cat = safe_string_value(book.get('category', '')).lower()
            title = safe_string_value(book.get('title', '')).lower()
            summary = safe_string_value(book.get('summary', '')).lower()
            
            # Check if book matches professional field
            field_match = False
            for keyword in field_words:
                if keyword in cat or keyword in title or keyword in summary:
                    field_match = True
                    break
            
            if field_match:
                recommendations.append(create_book_recommendation(book))
        
        # If still not enough matches, add general recommendations
        if len(recommendations) < top_n // 2:
            for _, book in result['recommendations'].iterrows():
                if len(recommendations) >= top_n:
                    break
                book_rec = create_book_recommendation(book)
                if book_rec not in recommendations:
                    recommendations.append(book_rec)

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
            'recommendations': recommendations,
            'total_matches': len(recommendations),
            'top_n_requested': top_n
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in professional and recommend: {str(e)}")

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