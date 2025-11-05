"""
Test script for Combined Caelio API
Test both Personality API and Caelio Care API on same server
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"
PERSONALITY_API = f"{BASE_URL}/personality"
CARE_API = f"{BASE_URL}/care"

async def test_combined_api():
    """Test combined Caelio API endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Combined Caelio API")
        
        # 1. Test main root endpoint
        print("\n1. Testing Main Root Endpoint...")
        async with session.get(f"{BASE_URL}/") as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Main API running: {result['message']}")
                print(f"   Services: {list(result['services'].keys())}")
            else:
                print(f"❌ Main API failed: {await resp.text()}")
        
        # 2. Test health check
        print("\n2. Testing Combined Health Check...")
        async with session.get(f"{BASE_URL}/health") as resp:
            if resp.status == 200:
                health = await resp.json()
                print(f"✅ Health check passed")
                print(f"   Personality: {health['services']['personality']}")
                print(f"   Care: {health['services']['care']}")
            else:
                print(f"❌ Health check failed: {await resp.text()}")
        
        # 3. Test Personality API
        print("\n3. Testing Personality API...")
        async with session.get(f"{PERSONALITY_API}/questions?question_type=discovery") as resp:
            if resp.status == 200:
                questions = await resp.json()
                print(f"✅ Personality API working - Got {len(questions)} discovery questions")
            else:
                print(f"❌ Personality API failed: {await resp.text()}")
        
        # 4. Test personality analysis
        print("\n4. Testing Personality Analysis...")
        personality_answers = {
            "Q1": "A", "Q2": "C", "Q3": "E"
        }
        
        async with session.post(f"{PERSONALITY_API}/analyze", json=personality_answers) as resp:
            if resp.status == 200:
                profile = await resp.json()
                primary_group = profile["primary_group"]
                print(f"✅ Personality analysis working")
                print(f"   Primary Group: {primary_group}")
                print(f"   Is Synthesizer: {profile['is_synthesizer']}")
            else:
                print(f"❌ Personality analysis failed: {await resp.text()}")
                primary_group = "Tri thức"  # Fallback
        
        # 5. Test Caelio Care registration
        print("\n5. Testing Caelio Care Registration...")
        register_data = {
            "email": "test@caelio.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
        
        async with session.post(f"{CARE_API}/auth/register", json=register_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result["access_token"]
                print(f"✅ Care registration successful! Token: {token[:20]}...")
            elif resp.status == 400 and "already registered" in await resp.text():
                # Try login instead
                login_data = {
                    "email": "test@caelio.com",
                    "password": "password123"
                }
                async with session.post(f"{CARE_API}/auth/login", json=login_data) as login_resp:
                    if login_resp.status == 200:
                        result = await login_resp.json()
                        token = result["access_token"]
                        print(f"✅ Care login successful! Token: {token[:20]}...")
                    else:
                        print(f"❌ Care login failed: {await login_resp.text()}")
                        return
            else:
                print(f"❌ Care registration failed: {await resp.text()}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 6. Test emotional questions
        print("\n6. Testing Emotional Assessment Questions...")
        async with session.get(f"{CARE_API}/emotional-test/questions") as resp:
            if resp.status == 200:
                questions = await resp.json()
                print(f"✅ Got {len(questions['questions'])} emotional questions")
            else:
                print(f"❌ Failed to get emotional questions: {await resp.text()}")
        
        # 7. Test emotional assessment
        print("\n7. Testing Emotional Assessment...")
        emotional_answers = {
            "Q1": 4, "Q2": 3, "Q3": 3, "Q4": 4, "Q5": 3,
            "Q6": 2, "Q7": 3, "Q8": 2, "Q9": 1
        }
        
        async with session.post(f"{CARE_API}/emotional-test/analyze", 
                               json=emotional_answers, 
                               params={"archetype": primary_group},
                               headers=headers) as resp:
            if resp.status == 200:
                profile = await resp.json()
                emotional_layer = profile["emotional_layer"]
                print(f"✅ Emotional assessment complete!")
                print(f"   Emotional Layer: {emotional_layer}")
                print(f"   MBI Score: {profile['mbi_score']}")
                print(f"   Archetype: {primary_group}")
            else:
                print(f"❌ Emotional assessment failed: {await resp.text()}")
                emotional_layer = "Hồi phục"  # Fallback
        
        # 8. Test book prescription (combining both systems)
        print("\n8. Testing Combined Book Prescription...")
        async with session.get(f"{CARE_API}/emotional-test/prescription/{emotional_layer}",
                               params={"archetype": primary_group}) as resp:
            if resp.status == 200:
                prescription = await resp.json()
                print(f"✅ Got prescription for {emotional_layer} + {primary_group}")
                print(f"   Books: {len(prescription['recommended_books'])}")
                print(f"   Sample: {prescription['recommended_books'][0] if prescription['recommended_books'] else 'None'}")
            else:
                print(f"❌ Prescription failed: {await resp.text()}")
        
        # 9. Test personality book recommendations
        print("\n9. Testing Personality Book Recommendations...")
        async with session.post(f"{PERSONALITY_API}/discover", json=personality_answers) as resp:
            if resp.status == 200:
                result = await resp.json()
                recommendations = result["recommendations"]
                print(f"✅ Personality recommendations: {len(recommendations)} books")
                if recommendations:
                    print(f"   Top book: {recommendations[0]['title']}")
            else:
                print(f"❌ Personality recommendations failed: {await resp.text()}")
        
        # 10. Test white book creation
        print("\n10. Testing White Book Creation...")
        book_data = {
            "title": f"Hành trình {primary_group} - {emotional_layer}",
            "category": "Tự truyện",
            "content": f"Đây là câu chuyện về hành trình từ {primary_group} đến {emotional_layer}. Mỗi ngày tôi học được thêm nhiều điều về bản thân...",
            "emotional_layer": emotional_layer,
            "prompt_used": "Hôm nay bạn biết ơn điều gì?",
            "tags": [primary_group.lower(), emotional_layer.lower(), "tự truyện"]
        }
        
        async with session.post(f"{CARE_API}/white-books/create", 
                               json=book_data, headers=headers) as resp:
            if resp.status == 200:
                book = await resp.json()
                print(f"✅ White book created: '{book['title']}'")
                print(f"   Layer: {book['emotional_layer']}")
            else:
                print(f"❌ White book creation failed: {await resp.text()}")
        
        # 11. Test system stats
        print("\n11. Testing System Statistics...")
        async with session.get(f"{PERSONALITY_API}/stats") as resp:
            if resp.status == 200:
                stats = await resp.json()
                print(f"✅ Personality API stats:")
                print(f"   Questions: {stats.get('discovery_questions', 0)} + {stats.get('professional_questions', 0)}")
                
        async with session.get(f"{CARE_API}/stats") as resp:
            if resp.status == 200:
                stats = await resp.json()
                print(f"✅ Care API stats:")
                print(f"   Users: {stats['users']}")
                print(f"   White books: {stats['white_books']['total']}")
        
        print("\n🎉 Combined API testing completed!")
        print("\n📊 SUMMARY:")
        print("   🧠 Personality API: Assessment + Book Recommendations")
        print("   💚 Caelio Care API: Emotional Assessment + White Books + Auth")
        print("   🌟 Combined: Comprehensive bibliotherapy system")
        print("\n🔗 ACCESS POINTS:")
        print(f"   📖 Main Docs: {BASE_URL}/docs")
        print(f"   🧠 Personality: {PERSONALITY_API}/docs")
        print(f"   💚 Care: {CARE_API}/docs")

if __name__ == "__main__":
    print("Make sure Combined Caelio API is running on localhost:8000")
    print("Command: python run_api.py")
    input("Press Enter to start testing...")
    
    asyncio.run(test_combined_api())