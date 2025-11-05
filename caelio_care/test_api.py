"""
Test script for Caelio Care API
Quick testing of all features
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8001"

async def test_caelio_care_api():
    """Test all Caelio Care API endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Caelio Care API")
        
        # 1. Test registration
        print("\n1. Testing User Registration...")
        register_data = {
            "email": "test@caelio.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
        
        async with session.post(f"{BASE_URL}/auth/register", json=register_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result["access_token"]
                print(f"✅ Registration successful! Token: {token[:20]}...")
            else:
                print(f"❌ Registration failed: {await resp.text()}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test emotional questions
        print("\n2. Testing Emotional Questions...")
        async with session.get(f"{BASE_URL}/emotional-test/questions") as resp:
            if resp.status == 200:
                questions = await resp.json()
                print(f"✅ Got {len(questions['questions'])} questions")
            else:
                print(f"❌ Failed to get questions: {await resp.text()}")
        
        # 3. Test emotional assessment
        print("\n3. Testing Emotional Assessment...")
        answers = {
            "Q1": 4, "Q2": 3, "Q3": 3, "Q4": 4, "Q5": 3,
            "Q6": 2, "Q7": 3, "Q8": 2, "Q9": 1
        }
        
        async with session.post(f"{BASE_URL}/emotional-test/analyze", 
                               json=answers, headers=headers) as resp:
            if resp.status == 200:
                profile = await resp.json()
                emotional_layer = profile["emotional_layer"]
                mbi_score = profile["mbi_score"]
                print(f"✅ Assessment complete!")
                print(f"   Emotional Layer: {emotional_layer}")
                print(f"   MBI Score: {mbi_score}")
                print(f"   PERMA: {profile['perma_score']}, DASS: {profile['dass_score']}")
            else:
                print(f"❌ Assessment failed: {await resp.text()}")
                emotional_layer = "Hồi phục"  # Fallback
        
        # 4. Test book prescription
        print("\n4. Testing Book Prescription...")
        async with session.get(f"{BASE_URL}/emotional-test/prescription/{emotional_layer}") as resp:
            if resp.status == 200:
                prescription = await resp.json()
                books = prescription["recommended_books"]
                prompts = prescription["writing_prompts"]
                print(f"✅ Got prescription for {emotional_layer}")
                print(f"   Recommended books: {len(books)}")
                print(f"   Writing prompts: {len(prompts)}")
                print(f"   Sample book: {books[0] if books else 'None'}")
            else:
                print(f"❌ Prescription failed: {await resp.text()}")
        
        # 5. Test white book creation
        print("\n5. Testing White Book Creation...")
        book_data = {
            "title": "Hành trình tìm lại chính mình",
            "category": "Tự truyện",
            "content": "Đây là câu chuyện về hành trình khám phá bản thân của tôi. Những ngày tháng khó khăn đã dạy tôi rất nhiều về sự kiên nhẫn và lòng biết ơn...",
            "emotional_layer": emotional_layer,
            "prompt_used": "Hôm nay bạn biết ơn điều gì?",
            "tags": ["tự truyện", "hồi phục", "biết ơn"]
        }
        
        async with session.post(f"{BASE_URL}/white-books/create", 
                               json=book_data, headers=headers) as resp:
            if resp.status == 200:
                book = await resp.json()
                book_id = book["book_id"]
                print(f"✅ White book created! ID: {book_id}")
                print(f"   Title: {book['title']}")
                print(f"   Layer: {book['emotional_layer']}")
            else:
                print(f"❌ Book creation failed: {await resp.text()}")
                return
        
        # 6. Test book publishing
        print("\n6. Testing Book Publishing...")
        async with session.put(f"{BASE_URL}/white-books/{book_id}/publish", 
                              headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Book published! {result['message']}")
            else:
                print(f"❌ Publishing failed: {await resp.text()}")
        
        # 7. Test getting published books
        print("\n7. Testing Published Books...")
        async with session.get(f"{BASE_URL}/white-books/published") as resp:
            if resp.status == 200:
                books = await resp.json()
                print(f"✅ Got {len(books)} published books")
                if books:
                    book = books[0]
                    print(f"   Latest: '{book['title']}' by {book['author_username']}")
            else:
                print(f"❌ Failed to get published books: {await resp.text()}")
        
        # 8. Test writing prompts
        print("\n8. Testing Writing Prompts...")
        async with session.get(f"{BASE_URL}/writing-prompts/{emotional_layer}") as resp:
            if resp.status == 200:
                prompts = await resp.json()
                print(f"✅ Got writing prompts for {emotional_layer}")
                for i, prompt in enumerate(prompts["prompts"], 1):
                    print(f"   {i}. {prompt}")
            else:
                print(f"❌ Failed to get prompts: {await resp.text()}")
        
        # 9. Test system stats
        print("\n9. Testing System Statistics...")
        async with session.get(f"{BASE_URL}/stats") as resp:
            if resp.status == 200:
                stats = await resp.json()
                print(f"✅ System stats:")
                print(f"   Users: {stats['users']}")
                print(f"   Emotional tests: {stats['emotional_tests']}")
                print(f"   White books: {stats['white_books']['total']} (published: {stats['white_books']['published']})")
                print(f"   Available layers: {stats['available_layers']}")
            else:
                print(f"❌ Failed to get stats: {await resp.text()}")
        
        print("\n🎉 All tests completed!")

if __name__ == "__main__":
    print("Make sure Caelio Care API is running on localhost:8001")
    print("And PostgreSQL database 'caelio_care' is available")
    input("Press Enter to start testing...")
    
    asyncio.run(test_caelio_care_api())