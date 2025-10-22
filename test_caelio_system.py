"""
Test cases cho hệ thống Caelio Personality
Kiểm tra tính chính xác theo tài liệu
"""

from caelio_personality_system import CaelioPersonalitySystem
from caelio_book_matcher import CaelioBookMatcher
import pandas as pd

def test_example_from_documentation():
    """
    Test ví dụ từ tài liệu:
    Kết quả mong đợi: Thinker–Synthesizer
    """
    system = CaelioPersonalitySystem()
    
    # Ví dụ từ tài liệu
    answers = {
        'Q1': 'C',  # Tri thức
        'Q2': 'D',  # Kiến tạo  
        'Q3': 'E',  # Synthesizer +1
        'Q4': 'C',  # Synthesizer +1
        'Q5': 'B',  # Tự do
        'Q6': 'E',  # Synthesizer +1
        'Q7': 'C',  # Tri thức
        'Q8': 'C'   # Synthesizer +1
    }
    
    profile = system.calculate_discovery_profile(answers)
    
    print("=== TEST VÍ DỤ TÀI LIỆU ===")
    print(f"Câu trả lời: {answers}")
    print(f"Điểm các nhóm: {profile['all_scores']}")
    print(f"Điểm Synthesizer: {profile['synthesizer_score']}")
    print(f"Kết quả: {profile['profile_name']}")
    print(f"Mong đợi: Tri thức–Synthesizer")
    
    # Kiểm tra
    assert profile['primary_group'] == 'Tri thức', f"Expected 'Tri thức', got '{profile['primary_group']}'"
    assert profile['synthesizer_score'] == 4, f"Expected 4, got {profile['synthesizer_score']}"
    assert profile['is_synthesizer'] == True, f"Expected True, got {profile['is_synthesizer']}"
    assert 'Synthesizer' in profile['profile_name'], f"Expected 'Synthesizer' in name, got '{profile['profile_name']}'"
    
    print("✅ PASS: Ví dụ tài liệu chính xác!")
    return profile

def test_pure_connector():
    """Test trường hợp thuần Kết nối"""
    system = CaelioPersonalitySystem()
    
    answers = {
        'Q1': 'A',  # Kết nối
        'Q2': 'A',  # Kết nối
        'Q3': 'A',  # Kết nối
        'Q4': 'A',  # Tri thức (đọc sâu)
        'Q5': 'A',  # Kết nối
        'Q6': 'A',  # Kết nối
        'Q7': 'A',  # Kết nối
        'Q8': 'A'   # Kết nối
    }
    
    profile = system.calculate_discovery_profile(answers)
    
    print("\n=== TEST PURE CONNECTOR ===")
    print(f"Kết quả: {profile['profile_name']}")
    print(f"Điểm Kết nối: {profile['all_scores']['Kết nối']}")
    print(f"Synthesizer: {profile['is_synthesizer']}")
    
    assert profile['primary_group'] == 'Kết nối'
    assert profile['is_synthesizer'] == False
    print("✅ PASS: Pure Connector chính xác!")
    return profile

def test_tie_breaker():
    """Test trường hợp hòa điểm - ưu tiên WHY"""
    system = CaelioPersonalitySystem()
    
    # Kết nối vs Tri thức hòa, nhưng Kết nối chiếm ưu thế trong WHY (Q1-Q3)
    answers = {
        'Q1': 'A',  # Kết nối - WHY
        'Q2': 'A',  # Kết nối - WHY  
        'Q3': 'C',  # Tri thức - WHY
        'Q4': 'A',  # Tri thức
        'Q5': 'A',  # Kết nối
        'Q6': 'C',  # Tri thức
        'Q7': 'A',  # Kết nối
        'Q8': 'B'   # Tri thức
    }
    
    profile = system.calculate_discovery_profile(answers)
    
    print("\n=== TEST TIE BREAKER ===")
    print(f"Điểm: {profile['all_scores']}")
    print(f"Kết quả: {profile['profile_name']}")
    print(f"WHY answers: Q1=A(Kết nối), Q2=A(Kết nối), Q3=C(Tri thức)")
    
    # Kết nối chiếm 2/3 trong WHY nên được ưu tiên
    assert profile['primary_group'] == 'Kết nối'
    print("✅ PASS: Tie breaker theo WHY chính xác!")
    return profile

def test_synthesizer_conditions():
    """Test các điều kiện kích hoạt Synthesizer"""
    system = CaelioPersonalitySystem()
    
    # Synthesizer score = 3, primary vs secondary chênh 1 -> should be Synthesizer
    answers = {
        'Q1': 'A',  # Kết nối
        'Q2': 'B',  # Tự do
        'Q3': 'E',  # Synthesizer +1
        'Q4': 'C',  # Synthesizer +1
        'Q5': 'C',  # Synthesizer +1
        'Q6': 'A',  # Kết nối
        'Q7': 'B',  # Tự do
        'Q8': 'A'   # Kết nối
    }
    
    profile = system.calculate_discovery_profile(answers)
    
    print("\n=== TEST SYNTHESIZER CONDITIONS ===")
    print(f"Điểm: {profile['all_scores']}")
    print(f"Synthesizer score: {profile['synthesizer_score']}")
    print(f"Chênh lệch điểm: {abs(profile['primary_score'] - profile['secondary_score'])}")
    print(f"Là Synthesizer: {profile['is_synthesizer']}")
    
    # Synthesizer score >= 3 và chênh lệch <= 1
    expected_synthesizer = profile['synthesizer_score'] >= 3 and abs(profile['primary_score'] - profile['secondary_score']) <= 1
    assert profile['is_synthesizer'] == expected_synthesizer
    print("✅ PASS: Điều kiện Synthesizer chính xác!")
    return profile

def test_book_matching():
    """Test matching sách theo tính cách"""
    matcher = CaelioBookMatcher()
    
    # Tạo dữ liệu sách mẫu
    sample_books = [
        {'product_id': 1, 'title': 'Cây Cam Ngọt Của Tôi', 'category': 'Tiểu Thuyết', 'authors': 'José Mauro'},
        {'product_id': 2, 'title': 'Thao Túng Tâm Lý', 'category': 'Sách tư duy - Kỹ năng sống', 'authors': 'Dale Carnegie'},
        {'product_id': 3, 'title': 'Marketing 4.0', 'category': 'Sách Marketing - Bán hàng', 'authors': 'Philip Kotler'},
        {'product_id': 4, 'title': 'Lịch Sử Việt Nam', 'category': 'Lịch sử', 'authors': 'Trần Trọng Kim'},
        {'product_id': 5, 'title': 'Triết Học Phương Đông', 'category': 'Triết học', 'authors': 'Alan Watts'},
    ]
    book_df = pd.DataFrame(sample_books)
    
    # Test với Connector profile
    connector_answers = {
        'Q1': 'A', 'Q2': 'A', 'Q3': 'A', 'Q4': 'A', 
        'Q5': 'A', 'Q6': 'A', 'Q7': 'A', 'Q8': 'A'
    }
    
    result = matcher.get_personalized_recommendations(connector_answers, book_df)
    
    print("\n=== TEST BOOK MATCHING ===")
    print(f"Profile: {result['profile']['profile_name']}")
    print(f"Tổng sách match: {result['total_matches']}")
    print("Top recommendations:")
    for _, book in result['recommendations'].head(3).iterrows():
        print(f"- {book['title']} ({book['category']}) - Score: {book['personality_match_score']:.2f}")
    
    # Sách về tâm lý/kỹ năng sống nên có điểm cao cho Connector
    psychology_books = result['recommendations'][
        result['recommendations']['category'] == 'Sách tư duy - Kỹ năng sống'
    ]
    
    assert len(psychology_books) > 0, "Should find psychology books for Connector"
    assert psychology_books.iloc[0]['personality_match_score'] >= 0.8, "Psychology books should have high score"
    
    print("✅ PASS: Book matching chính xác!")
    return result

def run_all_tests():
    """Chạy tất cả test cases"""
    print("🧪 CHẠY TẤT CẢ TEST CASES")
    print("="*50)
    
    try:
        test_example_from_documentation()
        test_pure_connector() 
        test_tie_breaker()
        test_synthesizer_conditions()
        test_book_matching()
        
        print("\n🎉 TẤT CẢ TEST CASES PASSED!")
        print("Hệ thống hoạt động chính xác theo tài liệu.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise e

def interactive_test():
    """Test tương tác"""
    system = CaelioPersonalitySystem()
    
    print("\n🎯 TEST TƯƠNG TÁC")
    print("Trả lời các câu hỏi để test hệ thống:")
    
    answers = {}
    for q_id, question_data in system.discovery_questions.items():
        print(f"\n{q_id}. {question_data['question']}")
        for choice_key, choice_data in question_data['choices'].items():
            print(f"  {choice_key}. {choice_data['text']}")
        
        while True:
            choice = input("Chọn (A/B/C/D/E): ").upper().strip()
            if choice in question_data['choices']:
                answers[q_id] = choice
                break
            print("Lựa chọn không hợp lệ!")
    
    profile = system.calculate_discovery_profile(answers)
    
    print(f"\n=== KẾT QUẢ ===")
    print(f"Profile: {profile['profile_name']}")
    print(f"English: {profile['english_name']}")
    print(f"Điểm các nhóm: {profile['all_scores']}")
    print(f"Synthesizer score: {profile['synthesizer_score']}")
    
    return profile

if __name__ == "__main__":
    # Chạy automated tests
    run_all_tests()
    
    # Tùy chọn chạy test tương tác
    print("\n" + "="*50)
    choice = input("Chạy test tương tác? (y/n): ").lower().strip()
    if choice == 'y':
        interactive_test()