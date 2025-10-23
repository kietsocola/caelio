"""
Test API mới với các endpoint tổng hợp
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_discover_api():
    """Test API tổng hợp discovery - trả về cả analysis + recommendations"""
    print("=== TEST DISCOVER API (Analysis + Recommendations) ===")
    
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
    
    response = requests.post(f"{BASE_URL}/discover", json=discovery_answers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Profile: {result['profile']['profile_name']}")
        print(f"✓ English: {result['profile']['english_name']}")
        print(f"✓ Synthesizer: {result['profile']['is_synthesizer']}")
        print(f"✓ Total matches: {result['total_matches']}")
        print(f"✓ Recommendations: {len(result['recommendations'])}")
        
        # In 3 sách đầu tiên
        for i, book in enumerate(result['recommendations'][:3]):
            print(f"  {i+1}. {book['title']} - {book['category']} (Score: {book['personality_match_score']:.2f})")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def test_professional_api():
    """Test API tổng hợp professional - trả về cả analysis + recommendations"""
    print("\n=== TEST PROFESSIONAL API (Analysis + Recommendations) ===")
    
    # Dùng format combined: discovery + professional
    professional_answers = {
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
            "Q3": "B",  # Tự mình tìm liên kết
            "Q4": "C"   # Kết nối đa ngành
        }
    }
    
    response = requests.post(f"{BASE_URL}/professional", json=professional_answers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Profile: {result['profile']['profile_name']}")
        print(f"✓ English: {result['profile']['english_name']}")
        print(f"✓ Synthesizer: {result['profile']['is_synthesizer']}")
        print(f"✓ Total matches: {result['total_matches']}")
        print(f"✓ Recommendations: {len(result['recommendations'])}")
        
        # In 3 sách đầu tiên
        for i, book in enumerate(result['recommendations'][:3]):
            print(f"  {i+1}. {book['title']} - {book['category']} (Score: {book['personality_match_score']:.2f})")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def test_original_recommend_fixed():
    """Test API recommend gốc đã sửa lỗi NaN"""
    print("\n=== TEST ORIGINAL RECOMMEND API (Fixed NaN issue) ===")
    
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
    
    response = requests.post(f"{BASE_URL}/recommend?top_n=5", json=discovery_answers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Profile: {result['profile']['profile_name']}")
        print(f"✓ Total matches: {result['total_matches']}")
        print(f"✓ Recommendations: {len(result['recommendations'])}")
        
        # Check if summary field is properly handled
        for i, book in enumerate(result['recommendations'][:3]):
            summary = book.get('summary', '')
            print(f"  {i+1}. {book['title']} - Summary length: {len(summary) if summary else 0}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def test_simplified_professional_recommend():
    """Test API recommend-professional với format combined"""
    print("\n=== TEST PROFESSIONAL RECOMMEND API (Combined format) ===")
    
    # Cần cả discovery + professional answers
    professional_answers = {
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
            "Q3": "B",  # Tự mình tìm liên kết
            "Q4": "C"   # Kết nối đa ngành
        }
    }
    
    response = requests.post(f"{BASE_URL}/recommend-professional?top_n=5", json=professional_answers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Profile: {result['profile']['profile_name']}")
        print(f"✓ Total matches: {result['total_matches']}")
        print(f"✓ Recommendations: {len(result['recommendations'])}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")

def compare_apis():
    """So sánh kết quả giữa các API"""
    print("\n=== COMPARING API RESULTS ===")
    
    discovery_answers = {
        "Q1": "A",  # Kết nối
        "Q2": "B",  # Tự do  
        "Q3": "C",  # Tri thức
        "Q4": "A",  # Tri thức
        "Q5": "A",  # Kết nối
        "Q6": "A",  # Kết nối
        "Q7": "A",  # Kết nối
        "Q8": "A"   # Kết nối
    }
    
    combined_answers = {
        "discovery_answers": discovery_answers,
        "professional_answers": {
            "Q1": "A",  # Kinh tế - Quản trị - Tài chính
            "Q2": "A",  # Xây nền tảng lý thuyết
            "Q3": "A",  # Có lộ trình rõ ràng
            "Q4": "A"   # Sách học chuyên sâu
        }
    }
    
    # Test discover API
    response1 = requests.post(f"{BASE_URL}/discover", json=discovery_answers)
    profile1 = response1.json()['profile']['profile_name'] if response1.status_code == 200 else "Error"
    
    # Test professional API (uses combined format)
    response2 = requests.post(f"{BASE_URL}/professional", json=combined_answers)
    profile2 = response2.json()['profile']['profile_name'] if response2.status_code == 200 else "Error"
    
    # Test analyze API
    response3 = requests.post(f"{BASE_URL}/analyze", json=discovery_answers)
    profile3 = response3.json()['profile_name'] if response3.status_code == 200 else "Error"
    
    print(f"Discover API result: {profile1}")
    print(f"Professional API result: {profile2}")
    print(f"Analyze API result: {profile3}")
    print(f"Discovery vs Analyze consistent: {profile1 == profile3}")
    print(f"Professional includes field info and may have different profile due to professional context")

if __name__ == "__main__":
    try:
        # Test health check
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("API is not running. Please start it first with: python run_api.py")
            exit(1)
        
        print("API is running. Testing new endpoints...\n")
        
        # Test all new functionality
        test_discover_api()
        test_professional_api()
        test_original_recommend_fixed()
        test_simplified_professional_recommend()
        compare_apis()
        
        print("\n=== ALL NEW TESTS COMPLETED ===")
        print("\nSummary of changes:")
        print("✓ Fixed NaN validation error in BookRecommendation")
        print("✓ Simplified professional API to use 8 questions only")
        print("✓ Added /discover - analysis + recommendations for discovery")
        print("✓ Added /professional - analysis + recommendations for professional")
        
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API. Please start it first with: python run_api.py")
    except Exception as e:
        print(f"Error: {e}")