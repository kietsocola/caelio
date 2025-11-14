"""
Emotional Assessment System for Caelio Care
Based on PERMA-DASS model with 4 emotional layers
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import pandas as pd
import os
import random

class EmotionalAnswers(BaseModel):
    Q1: int  # 1-5 scale for all questions
    Q2: int
    Q3: int
    Q4: int
    Q5: int
    Q6: int
    Q7: int
    Q8: int
    Q9: int

class EmotionalProfile(BaseModel):
    perma_score: float
    dass_score: float
    mbi_score: float  # Mental Balance Index
    emotional_layer: str
    layer_description: str
    reading_goal: str
    archetype_influence: Optional[str] = None

class EmotionalTestSystem:
    def __init__(self):
        self.questions = {
            "Q1": {
                "question": "Gần đây tôi thường cảm thấy biết ơn, nhẹ nhõm hoặc tìm thấy niềm vui trong những điều nhỏ bé.",
                "group": "PERMA",
                "component": "Positive Emotion",
                "layer": "Hồi phục / Tái sinh",
                "why": "Đọc để nuôi dưỡng cảm xúc tích cực, tìm lại niềm vui giản đơn trong cuộc sống.",
                "how": "Đọc chậm, văn chương hoặc thơ mang năng lượng bình an."
            },
            "Q2": {
                "question": "Tôi dễ tập trung và hòa mình vào những việc mình đang làm (học, đọc, làm việc...).",
                "group": "PERMA",
                "component": "Engagement",
                "layer": "Hồi phục",
                "why": "Đọc để khôi phục trạng thái 'flow', kết nối lại với bản thân.",
                "how": "Đọc có nghi thức, mindfulness, ritual đọc – viết mỗi ngày."
            },
            "Q3": {
                "question": "Tôi cảm thấy được yêu thương, lắng nghe và thấu hiểu bởi những người xung quanh.",
                "group": "PERMA",
                "component": "Relationships",
                "layer": "Chấp nhận / Hồi phục",
                "why": "Đọc để tìm lại cảm giác thuộc về, được đồng cảm và sẻ chia.",
                "how": "Đọc truyện nhân văn, các tác phẩm về lòng tốt và tình người."
            },
            "Q4": {
                "question": "Tôi cảm thấy cuộc sống của mình vẫn đang có ý nghĩa, dù có khó khăn.",
                "group": "PERMA",
                "component": "Meaning",
                "layer": "Tái sinh",
                "why": "Đọc để tìm lại mục đích sống, tái khám phá ý nghĩa hiện hữu.",
                "how": "Đọc triết lý sống, văn học hiện sinh, tự truyện khai sáng."
            },
            "Q5": {
                "question": "Tôi tự hào về những điều mình đã và đang cố gắng thực hiện.",
                "group": "PERMA",
                "component": "Achievement",
                "layer": "Tái sinh",
                "why": "Đọc để củng cố niềm tin vào năng lực bản thân, khích lệ ý chí tiến lên.",
                "how": "Đọc self-help truyền cảm hứng, hồi ký vượt khó, sách hành động."
            },
            "Q6": {
                "question": "Dạo này tôi thấy khó thư giãn, dù đã cố gắng nghỉ ngơi.",
                "group": "DASS",
                "component": "Stress",
                "layer": "Nhận diện",
                "why": "Đọc để giải toả căng thẳng, tìm lại hơi thở và nhịp sống chậm.",
                "how": "Đọc thiền, sách về tĩnh lặng, các tác phẩm hướng nội."
            },
            "Q7": {
                "question": "Tôi thường lo lắng hoặc sợ mắc sai lầm, ngay cả trong việc nhỏ.",
                "group": "DASS",
                "component": "Anxiety",
                "layer": "Nhận diện / Chấp nhận",
                "why": "Đọc để giảm bớt nỗi sợ, học cách chấp nhận và tự tin hơn.",
                "how": "Đọc tâm lý học ứng dụng, truyện dám sống – dám làm."
            },
            "Q8": {
                "question": "Tôi thấy ít hứng thú với những điều từng khiến mình vui.",
                "group": "DASS",
                "component": "Depression",
                "layer": "Nhận diện",
                "why": "Đọc để đánh thức lại cảm xúc và lòng biết ơn với cuộc sống.",
                "how": "Đọc hồi ký phục hồi, văn học nhân sinh, những câu chuyện vượt tối."
            },
            "Q9": {
                "question": "Gần đây tôi cảm thấy kiệt sức, như thể mọi nỗ lực đều không còn ý nghĩa.",
                "group": "DASS",
                "component": "Burnout",
                "layer": "Chấp nhận / Hồi phục",
                "why": "Đọc để hồi phục năng lượng tinh thần, tìm lại niềm tin vào giá trị của bản thân.",
                "how": "Đọc tản văn nhẹ, sách nói về cân bằng cuộc sống, hoặc hành trình 'nghỉ ngơi đúng nghĩa'."
            }
        }
        
        self.layer_prescriptions = {
            "Nhận diện": {
                "goal": "Gọi tên cảm xúc, hợp thức hóa nỗi buồn.",
                "keywords": [
                    "tâm lý", "cảm xúc", "trầm cảm", "buồn", "stress", "lo âu",
                    "nhận thức", "mindfulness", "thiền", "suy tư", "tĩnh lặng",
                    "hồi ký", "nhật ký", "tản văn", "văn học", "nhân sinh"
                ],
                "movies": ["About Time", "Little Women", "Lost in Translation"],
                "writing_prompts": [
                    "Điều khiến bạn mệt mỏi nhất gần đây là gì?",
                    "Nếu bạn được phép nói thật, bạn đang cảm thấy..."
                ]
            },
            "Chấp nhận": {
                "goal": "Đối thoại và sống cùng cảm xúc.",
                "keywords": [
                    "chấp nhận", "yêu thương", "tha thứ", "không hoàn hảo", "tự ái",
                    "tâm lý học", "phát triển bản thân", "cân bằng", "sống chậm",
                    "triết lý", "tình yêu", "mối quan hệ", "gia đình"
                ],
                "movies": ["The Secret Life of Walter Mitty", "Inside Out"],
                "writing_prompts": [
                    "Cảm xúc này đang dạy bạn điều gì?",
                    "Bạn sẽ ôm lấy phần tổn thương ấy như thế nào?"
                ]
            },
            "Hồi phục": {
                "goal": "Tái kết nối năng lượng và tìm lại nhịp sống.",
                "keywords": [
                    "hồi phục", "chữa lành", "năng lượng", "sức khỏe", "tinh thần",
                    "ikigai", "flow", "hạnh phúc", "biết ơn", "niềm vui",
                    "tĩnh lặng", "meditation", "yoga", "self-care", "balance"
                ],
                "movies": ["Eat Pray Love", "Soul (Pixar)"],
                "writing_prompts": [
                    "Hôm nay bạn biết ơn điều gì?",
                    "Bạn đã làm điều nhỏ nào khiến bản thân thấy dễ chịu hơn?"
                ]
            },
            "Tái sinh": {
                "goal": "Chuyển hóa tổn thương thành sáng tạo.",
                "keywords": [
                    "thay đổi", "biến đổi", "thành công", "động lực", "mục tiêu",
                    "can đảm", "dũng cảm", "vượt khó", "resilience", "growth",
                    "habits", "kỹ năng", "hành động", "chiến thắng", "truyền cảm hứng"
                ],
                "movies": ["The Pursuit of Happyness", "Good Will Hunting"],
                "writing_prompts": [
                    "Nếu viết lại hành trình của mình, bạn muốn đặt tên cuốn sách là gì?",
                    "Điều bạn muốn gửi cho ai đó đang ở vị trí cũ của bạn"
                ]
            }
        }
        
        # Load book database once during initialization
        self.books_df = self._load_book_database()
    
    def _load_book_database(self):
        """Load book database with fallback options"""
        # Try multiple paths
        possible_paths = [
            'dataset/books_full_data.csv',
            '../dataset/books_full_data.csv',
            'books_full_data.csv',
            'v2/labeled_books_v2.csv'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    return pd.read_csv(path)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    continue
        
        # Return empty DataFrame if no file found
        print("Warning: Book database not found, using empty dataset")
        return pd.DataFrame()
    
    def _load_nha_sach_xua_books(self):
        """Load nha_sach_xua books specifically"""
        nsx_paths = [
            'crawl_data/nha_sach_xua/data_crawl_nha_sach_xua.csv',
            '../crawl_data/nha_sach_xua/data_crawl_nha_sach_xua.csv',
            'data_crawl_nha_sach_xua.csv'
        ]
        
        for path in nsx_paths:
            if os.path.exists(path):
                try:
                    return pd.read_csv(path)
                except Exception as e:
                    print(f"Error loading nha_sach_xua {path}: {e}")
                    continue
        
        return pd.DataFrame()
    
    def _safe_string_value(self, value, default=''):
        """Safely convert value to string, handling NaN"""
        if pd.isna(value):
            return default
        return str(value) if value is not None else default
    
    def _search_books_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search books in database by keywords, prioritizing top 2 nha_sach_xua books"""
        if self.books_df.empty:
            return []
        
        # Load nha_sach_xua books
        nsx_df = self._load_nha_sach_xua_books()
        
        all_books = []
        
        # Get product_ids from nha_sach_xua to identify them
        nsx_product_ids = set()
        if not nsx_df.empty:
            nsx_product_ids = set(str(pid) for pid in nsx_df['product_id'].dropna())
        
        for _, book in self.books_df.iterrows():
            title = self._safe_string_value(book.get('title', '')).lower()
            category = self._safe_string_value(book.get('category', '')).lower()
            summary = self._safe_string_value(book.get('summary', '')).lower()
            content = self._safe_string_value(book.get('content', '')).lower()
            
            # Calculate keyword match score
            match_score = 0.0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title:
                    match_score += 3  # Title match is most important
                if keyword_lower in category:
                    match_score += 2  # Category match is very important
                if keyword_lower in summary:
                    match_score += 1  # Summary match
                if keyword_lower in content:
                    match_score += 0.5  # Content match
            
            # Quality factors
            avg_rating = float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else 0
            n_review = int(book.get('n_review', 0)) if pd.notna(book.get('n_review')) else 0
            
            rating_boost = (avg_rating / 5.0) * 0.3 if avg_rating > 0 else 0
            review_boost = min(n_review / 1000, 1.0) * 0.2 if n_review > 0 else 0
            
            final_score = match_score + rating_boost + review_boost
            
            # Check if book is from nha_sach_xua
            product_id_str = self._safe_string_value(book.get('product_id', ''))
            is_nsx_book = product_id_str in nsx_product_ids
            
            if final_score > 0.3:  # Threshold for inclusion
                book_dict = {
                    'product_id': product_id_str,
                    'title': self._safe_string_value(book.get('title', '')),
                    'authors': self._safe_string_value(book.get('authors', '')),
                    'category': self._safe_string_value(book.get('category', '')),
                    'summary': self._safe_string_value(book.get('summary', '')),
                    'avg_rating': avg_rating,
                    'n_review': n_review,
                    'cover_link': self._safe_string_value(book.get('cover_link', '')),
                    'match_score': final_score,
                    'is_nsx_book': is_nsx_book
                }
                all_books.append(book_dict)
        
        # Sort all books by score
        all_books.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Separate nha_sach_xua books
        nsx_books = [b for b in all_books if b['is_nsx_book']]
        regular_books = [b for b in all_books if not b['is_nsx_book']]
        
        # Take top 2 nha_sach_xua books (if available)
        top_nsx = nsx_books[:min(2, len(nsx_books))]
        
        # Take all other books sorted by score
        remaining_nsx = nsx_books[2:]
        all_other_books = regular_books + remaining_nsx
        all_other_books.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Build final result: insert nsx books in the middle
        if len(top_nsx) == 0:
            # No nsx books, return top scoring books
            return all_other_books[:limit]
        elif len(top_nsx) == 1:
            # 1 nsx book: put it around position limit//2
            insert_pos = min(limit // 2, len(all_other_books))
            final_results = all_other_books[:insert_pos] + top_nsx + all_other_books[insert_pos:]
            return final_results[:limit]
        else:
            # 2 nsx books: spread them in middle third of results
            # Position 1st nsx at ~1/3, 2nd nsx at ~2/3
            first_insert = min(limit // 3, len(all_other_books))
            second_insert = min(2 * limit // 3, len(all_other_books) + 1)
            
            # Insert first nsx book
            final_results = all_other_books[:first_insert] + [top_nsx[0]] + all_other_books[first_insert:]
            
            # Insert second nsx book (adjust position since we added one book)
            final_results = final_results[:second_insert] + [top_nsx[1]] + final_results[second_insert:]
            
            return final_results[:limit]
    
    def calculate_emotional_profile(self, answers: Dict[str, int], archetype: Optional[str] = None) -> EmotionalProfile:
        """Calculate emotional profile from answers"""
        
        # Calculate PERMA score (Q1-Q5, positive emotions)
        perma_scores = [answers[f"Q{i}"] for i in range(1, 6)]
        perma_avg = sum(perma_scores) / len(perma_scores)
        
        # Calculate DASS score (Q6-Q9, negative emotions, reverse scale)
        dass_scores = [6 - answers[f"Q{i}"] for i in range(6, 10)]  # Reverse scale
        dass_avg = sum(dass_scores) / len(dass_scores)
        
        # Calculate Mental Balance Index (MBI = PERMA - DASS)
        mbi_score = perma_avg - (6 - dass_avg)  # Convert DASS back to negative
        
        # Determine emotional layer based on MBI score
        if mbi_score <= -1.0:
            layer = "Nhận diện"
        elif mbi_score <= 0:
            layer = "Chấp nhận"
        elif mbi_score <= 1.0:
            layer = "Hồi phục"
        else:
            layer = "Tái sinh"
        
        prescription = self.layer_prescriptions[layer]
        
        return EmotionalProfile(
            perma_score=round(perma_avg, 2),
            dass_score=round(6 - dass_avg, 2),  # Convert back to original scale
            mbi_score=round(mbi_score, 2),
            emotional_layer=layer,
            layer_description=prescription["goal"],
            reading_goal=prescription["goal"],
            archetype_influence=archetype
        )
    
    def get_book_prescription(self, emotional_layer: str, archetype: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get book prescription for emotional layer with real book data"""
        prescription = self.layer_prescriptions.get(emotional_layer, self.layer_prescriptions["Nhận diện"])
        
        # Get base keywords for emotional layer
        base_keywords = prescription["keywords"].copy()
        
        # Add archetype-specific keywords if provided
        if archetype:
            archetype_keywords = {
                "Kết nối": ["tâm lý", "mối quan hệ", "gia đình", "tình cảm", "kết nối", "yêu thương", "đồng cảm"],
                "Tự do": ["du lịch", "tự do", "khám phá", "sáng tạo", "nghệ thuật", "phong cách sống", "cá tính"],
                "Tri thức": ["triết học", "khoa học", "lịch sử", "nghiên cứu", "tri thức", "học thuật", "tư duy"],
                "Chinh phục": ["lãnh đạo", "thành công", "chiến lược", "mục tiêu", "động lực", "chinh phục", "thách thức"],
                "Kiến tạo": ["kỹ năng", "kinh doanh", "khởi nghiệp", "phát triển", "xây dựng", "thực hành", "ứng dụng"]
            }
            
            if archetype in archetype_keywords:
                base_keywords.extend(archetype_keywords[archetype])
        
        # Search real books from database
        recommended_books = self._search_books_by_keywords(base_keywords, limit=limit)
        
        return {
            "emotional_layer": emotional_layer,
            "goal": prescription["goal"],
            "recommended_books": recommended_books,  # Now returns real book data with full info
            "recommended_movies": prescription["movies"],
            "writing_prompts": prescription["writing_prompts"],
            "archetype_applied": archetype,
            "keywords_used": base_keywords[:10]  # Show first 10 keywords used for search
        }