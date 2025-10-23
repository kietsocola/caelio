"""
Caelio API Client Example
Ví dụ cách sử dụng API từ frontend
"""

import requests
import json

class CaelioAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def health_check(self):
        """Kiểm tra API có hoạt động không"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_questions(self):
        """Lấy tất cả câu hỏi"""
        response = requests.get(f"{self.base_url}/questions")
        return response.json()
    
    def get_question(self, question_id):
        """Lấy câu hỏi cụ thể"""
        response = requests.get(f"{self.base_url}/questions/{question_id}")
        return response.json()
    
    def analyze_personality(self, answers):
        """
        Phân tích tính cách
        answers: dict với keys Q1-Q8 và values A-E
        """
        response = requests.post(
            f"{self.base_url}/analyze",
            json=answers
        )
        return response.json()
    
    def get_recommendations(self, answers, top_n=20):
        """
        Lấy gợi ý sách
        answers: dict với keys Q1-Q8 và values A-E
        """
        response = requests.post(
            f"{self.base_url}/recommend",
            json=answers,
            params={"top_n": top_n}
        )
        return response.json()
    
    def get_personality_groups(self):
        """Lấy danh sách nhóm tính cách"""
        response = requests.get(f"{self.base_url}/groups")
        return response.json()
    
    def get_stats(self):
        """Lấy thống kê hệ thống"""
        response = requests.get(f"{self.base_url}/stats")
        return response.json()

# === DEMO USAGE ===

def demo_api_usage():
    """Demo cách sử dụng API"""
    
    client = CaelioAPIClient()
    
    print("=== CAELIO API DEMO ===\n")
    
    # 1. Health check
    print("1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    print()
    
    # 2. Lấy câu hỏi
    print("2. Getting Questions:")
    questions = client.get_questions()
    print(f"Có {len(questions)} câu hỏi")
    
    # In câu hỏi đầu tiên
    first_q = questions["Q1"]
    print(f"Câu hỏi 1: {first_q['question']}")
    for choice_id, choice in first_q['choices'].items():
        print(f"  {choice_id}. {choice['text']}")
    print()
    
    # 3. Test với ví dụ
    print("3. Testing with Example Answers:")
    example_answers = {
        "Q1": "C", "Q2": "D", "Q3": "E", "Q4": "C",
        "Q5": "B", "Q6": "E", "Q7": "C", "Q8": "C"
    }
    
    # Phân tích tính cách
    profile = client.analyze_personality(example_answers)
    print(f"Profile: {profile['profile_name']}")
    print(f"Primary: {profile['primary_group']} ({profile['primary_score']} điểm)")
    print(f"Is Synthesizer: {profile['is_synthesizer']}")
    print()
    
    # 4. Lấy gợi ý sách
    print("4. Getting Book Recommendations:")
    try:
        recommendations = client.get_recommendations(example_answers, top_n=5)
        print(f"Profile: {recommendations['profile']['profile_name']}")
        print(f"Tìm thấy {recommendations['total_matches']} sách phù hợp")
        
        print("\nTop 5 sách:")
        for i, book in enumerate(recommendations['recommendations'][:5]):
            print(f"{i+1}. {book['title']}")
            print(f"   Tác giả: {book['authors']}")
            print(f"   Thể loại: {book['category']}")
            print(f"   Độ phù hợp: {book['personality_match_score']:.0%}")
            print()
    
    except Exception as e:
        print(f"Không thể lấy gợi ý sách: {e}")
        print("(Có thể do không tìm thấy file dữ liệu)")
    
    # 5. Stats
    print("5. System Stats:")
    stats = client.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

# === JAVASCRIPT/REACT EXAMPLE ===

js_example = '''
// JavaScript/React example
class CaelioAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async getQuestions() {
    const response = await fetch(`${this.baseUrl}/questions`);
    return response.json();
  }
  
  async analyzePersonality(answers) {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answers)
    });
    return response.json();
  }
  
  async getRecommendations(answers, topN = 20) {
    const response = await fetch(`${this.baseUrl}/recommend?top_n=${topN}`, {
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answers)
    });
    return response.json();
  }
}

// Usage in React
const api = new CaelioAPI();

// Get questions for quiz
const questions = await api.getQuestions();

// Submit answers and get profile
const answers = {
  Q1: "A", Q2: "B", Q3: "C", Q4: "D",
  Q5: "E", Q6: "A", Q7: "B", Q8: "C"
};

const profile = await api.analyzePersonality(answers);
const recommendations = await api.getRecommendations(answers, 10);
'''

def save_js_example():
    """Lưu ví dụ JavaScript"""
    with open("api_client_example.js", "w", encoding="utf-8") as f:
        f.write(js_example)
    print("Đã lưu ví dụ JavaScript vào api_client_example.js")

if __name__ == "__main__":
    demo_api_usage()
    save_js_example()