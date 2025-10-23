"""
Test API với cả 2 loại câu hỏi: Discovery và Professional
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_discovery_questions():
    """Test lấy câu hỏi hành trình khám phá"""
    print("=== DISCOVERY QUESTIONS ===")
    
    # Lấy tất cả câu hỏi discovery
    response = requests.get(f"{BASE_URL}/questions?question_type=discovery")
    if response.status_code == 200:
        questions = response.json()
        print(f"Có {len(questions)} câu hỏi discovery")
        
        # In câu hỏi đầu tiên
        if 'Q1' in questions:
            q1 = questions['Q1']
            print(f"\nQ1: {q1['question']}")
            for choice_id, choice_data in q1['choices'].items():
                print(f"  {choice_id}. {choice_data['text']} -> {choice_data['group']}")
    else:
        print(f"Error: {response.status_code}")

def test_professional_questions():
    """Test lấy câu hỏi hành trình chuyên ngành"""
    print("\n=== PROFESSIONAL QUESTIONS ===")
    
    # Lấy tất cả câu hỏi professional
    response = requests.get(f"{BASE_URL}/questions?question_type=professional")
    if response.status_code == 200:
        questions = response.json()
        print(f"Có {len(questions)} câu hỏi professional")
        
        # In câu hỏi đầu tiên
        if 'Q1' in questions:
            q1 = questions['Q1']
            print(f"\nQ1: {q1['question']}")
            for choice_id, choice_data in q1['choices'].items():
                print(f"  {choice_id}. {choice_data['text']} -> field: {choice_data.get('field', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")

def test_discovery_analysis():
    """Test phân tích tính cách hành trình khám phá"""
    print("\n=== DISCOVERY ANALYSIS ===")
    
    # Ví dụ từ documentation
    discovery_answers = {
        "Q1": "C",
        "Q2": "D", 
        "Q3": "E",
        "Q4": "C",
        "Q5": "B",
        "Q6": "E",
        "Q7": "C",
        "Q8": "C"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=discovery_answers)
    if response.status_code == 200:
        profile = response.json()
        print(f"Profile: {profile['profile_name']}")
        print(f"English: {profile['english_name']}")
        print(f"Synthesizer: {profile['is_synthesizer']}")
        print(f"Scores: {profile['all_scores']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_professional_analysis():
    """Test phân tích tính cách hành trình chuyên ngành"""
    print("\n=== PROFESSIONAL ANALYSIS ===")
    
    combined_answers = {
        "discovery_answers": {
            "Q1": "C",
            "Q2": "D", 
            "Q3": "E",
            "Q4": "C",
            "Q5": "B",
            "Q6": "E",
            "Q7": "C",
            "Q8": "C"
        },
        "professional_answers": {
            "Q1": "A",  # Kinh tế - Quản trị - Tài chính
            "Q2": "B",  # Giải quyết vấn đề thực tế
            "Q3": "B",  # Tự mình tìm liên kết (synthesizer potential)
            "Q4": "C"   # Kết nối đa ngành (synthesizer)
        }
    }
    
    response = requests.post(f"{BASE_URL}/analyze-professional", json=combined_answers)
    if response.status_code == 200:
        profile = response.json()
        print(f"Profile: {profile['profile_name']}")
        print(f"Field: {profile['field']}")
        print(f"Motivation: {profile['motivation']}")
        print(f"Learning Style: {profile['learning_style']}")
        print(f"Presentation: {profile['presentation_preference']}")
        print(f"Professional Synthesizer Indicators: {profile['professional_synthesizer_indicators']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_professional_recommendations():
    """Test gợi ý sách cho hành trình chuyên ngành"""
    print("\n=== PROFESSIONAL RECOMMENDATIONS ===")
    
    combined_answers = {
        "discovery_answers": {
            "Q1": "C",
            "Q2": "D", 
            "Q3": "E",
            "Q4": "C",
            "Q5": "B",
            "Q6": "E",
            "Q7": "C",
            "Q8": "C"
        },
        "professional_answers": {
            "Q1": "A",
            "Q2": "B",
            "Q3": "B",
            "Q4": "C"
        }
    }
    
    response = requests.post(f"{BASE_URL}/recommend-professional", json=combined_answers)
    if response.status_code == 200:
        result = response.json()
        print(f"Profile: {result['profile']['profile_name']}")
        print(f"Total matches: {result['total_matches']}")
        print(f"Recommendations: {len(result['recommendations'])}")
        
        # In 3 sách đầu tiên
        for i, book in enumerate(result['recommendations'][:3]):
            print(f"  {i+1}. {book['title']} - {book['category']} (Score: {book['personality_match_score']:.2f})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_stats():
    """Test endpoint stats"""
    print("\n=== SYSTEM STATS ===")
    
    response = requests.get(f"{BASE_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Discovery questions: {stats['discovery_questions']}")
        print(f"Professional questions: {stats['professional_questions']}")
        print(f"Total questions: {stats['total_questions']}")
        print(f"Journey types: {stats['journey_types']}")
        print(f"Personality groups: {stats['total_personality_groups']}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    try:
        # Test health check
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("API is not running. Please start it first with: python run_api.py")
            exit(1)
        
        print("API is running. Testing all endpoints...\n")
        
        # Test all functions
        test_discovery_questions()
        test_professional_questions()
        test_discovery_analysis()
        test_professional_analysis()
        test_professional_recommendations()
        test_stats()
        
        print("\n=== ALL TESTS COMPLETED ===")
        
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API. Please start it first with: python run_api.py")
    except Exception as e:
        print(f"Error: {e}")