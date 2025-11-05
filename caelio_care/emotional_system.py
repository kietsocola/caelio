"""
Emotional Assessment System for Caelio Care
Based on PERMA-DASS model with 4 emotional layers
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json

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
                "books": [
                    "Tôi nói gì khi nói về chạy bộ (Haruki Murakami)",
                    "Đi tìm lẽ sống (Viktor Frankl)",
                    "Thất lạc cõi người (Dazai Osamu)"
                ],
                "movies": ["About Time", "Little Women", "Lost in Translation"],
                "writing_prompts": [
                    "Điều khiến bạn mệt mỏi nhất gần đây là gì?",
                    "Nếu bạn được phép nói thật, bạn đang cảm thấy..."
                ]
            },
            "Chấp nhận": {
                "goal": "Đối thoại và sống cùng cảm xúc.",
                "books": [
                    "Yêu những điều không hoàn hảo (Haemin Sunim)",
                    "Muôn kiếp nhân sinh (Nguyên Phong)",
                    "The Gifts of Imperfection (Brené Brown)"
                ],
                "movies": ["The Secret Life of Walter Mitty", "Inside Out"],
                "writing_prompts": [
                    "Cảm xúc này đang dạy bạn điều gì?",
                    "Bạn sẽ ôm lấy phần tổn thương ấy như thế nào?"
                ]
            },
            "Hồi phục": {
                "goal": "Tái kết nối năng lượng và tìm lại nhịp sống.",
                "books": [
                    "Ikigai (Héctor García)",
                    "Sức mạnh của sự tĩnh lặng (Eckhart Tolle)",
                    "Stillness is the Key (Ryan Holiday)"
                ],
                "movies": ["Eat Pray Love", "Soul (Pixar)"],
                "writing_prompts": [
                    "Hôm nay bạn biết ơn điều gì?",
                    "Bạn đã làm điều nhỏ nào khiến bản thân thấy dễ chịu hơn?"
                ]
            },
            "Tái sinh": {
                "goal": "Chuyển hóa tổn thương thành sáng tạo.",
                "books": [
                    "Can đảm bước tiếp (Brené Brown)",
                    "Atomic Habits (James Clear)",
                    "Hành trình về phương Đông (Nguyên Phong)"
                ],
                "movies": ["The Pursuit of Happyness", "Good Will Hunting"],
                "writing_prompts": [
                    "Nếu viết lại hành trình của mình, bạn muốn đặt tên cuốn sách là gì?",
                    "Điều bạn muốn gửi cho ai đó đang ở vị trí cũ của bạn"
                ]
            }
        }
    
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
    
    def get_book_prescription(self, emotional_layer: str, archetype: Optional[str] = None) -> Dict[str, Any]:
        """Get book prescription for emotional layer"""
        prescription = self.layer_prescriptions.get(emotional_layer, self.layer_prescriptions["Nhận diện"])
        
        # Customize based on archetype if provided
        books = prescription["books"].copy()
        
        if archetype:
            # Add archetype-specific adjustments
            archetype_books = {
                "Kết nối": ["Tâm lý học gia đình", "Sách về mối quan hệ", "Truyện tình cảm"],
                "Tự do": ["Du ký", "Sách về tự do cá nhân", "Nghệ thuật sống"],
                "Tri thức": ["Triết học", "Khoa học nhận thức", "Sách học thuật"],
                "Chinh phục": ["Sách lãnh đạo", "Truyền cảm hứng", "Hồi ký thành công"],
                "Kiến tạo": ["Self-help", "Kỹ năng thực tế", "Sách kinh doanh"]
            }
            
            if archetype in archetype_books:
                books.extend(archetype_books[archetype])
        
        return {
            "emotional_layer": emotional_layer,
            "goal": prescription["goal"],
            "recommended_books": books,
            "recommended_movies": prescription["movies"],
            "writing_prompts": prescription["writing_prompts"]
        }