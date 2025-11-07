"""
Test script for White Books API with chapters
"""
import requests
import json

BASE_URL = "http://localhost:8000/care"

# Test credentials
TEST_USER = {
    "username": "testuser1",
    "email": "test1@example.com",
    "password": "testpass123",
    "full_name": "Test User 1"
}

def test_white_books():
    """Test white books functionality"""
    
    print("🧪 Testing White Books API")
    print("=" * 60)
    
    # 1. Register or Login
    print("\n1️⃣ Login...")
    try:
        # Try to register
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 200:
            print("✅ Registered new user")
        else:
            # User exists, login
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": TEST_USER["username"], "password": TEST_USER["password"]}
            )
            print("✅ Logged in existing user")
        
        data = response.json()
        token = data["access_token"]
        print(f"   Token: {token[:30]}...")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Create a book
    print("\n2️⃣ Creating a white book...")
    book_data = {
        "title": "My Healing Journey",
        "cover_image": "https://example.com/cover.jpg",
        "description": "A personal story about overcoming anxiety",
        "emotional_layer": "Layer 1",
        "tags": ["healing", "hope", "anxiety"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/white-books/create", json=book_data, headers=headers)
        response.raise_for_status()
        book = response.json()
        book_id = book["id"]
        print(f"✅ Created book ID: {book_id}")
        print(f"   Title: {book['title']}")
        print(f"   Description: {book['description']}")
    except Exception as e:
        print(f"❌ Book creation failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return
    
    # 3. Add Chapter 1
    print("\n3️⃣ Adding Chapter 1...")
    chapter1_data = {
        "chapter_number": 1,
        "chapter_title": "The Dark Days",
        "content": "It all started on a rainy Monday morning when I woke up feeling overwhelmed..."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/white-books/{book_id}/chapters",
            json=chapter1_data,
            headers=headers
        )
        response.raise_for_status()
        chapter1 = response.json()
        print(f"✅ Added Chapter 1")
        print(f"   Title: {chapter1['chapter_title']}")
        print(f"   Content preview: {chapter1['content'][:50]}...")
    except Exception as e:
        print(f"❌ Chapter 1 creation failed: {e}")
        if hasattr(e, 'response'):
            print(f"   Response: {e.response.text}")
        return
    
    # 4. Add Chapter 2
    print("\n4️⃣ Adding Chapter 2...")
    chapter2_data = {
        "chapter_number": 2,
        "chapter_title": "Finding Hope",
        "content": "The turning point came when I discovered bibliotherapy and started reading..."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/white-books/{book_id}/chapters",
            json=chapter2_data,
            headers=headers
        )
        response.raise_for_status()
        chapter2 = response.json()
        print(f"✅ Added Chapter 2")
        print(f"   Title: {chapter2['chapter_title']}")
    except Exception as e:
        print(f"❌ Chapter 2 creation failed: {e}")
        return
    
    # 5. Get all chapters
    print("\n5️⃣ Getting all chapters...")
    try:
        response = requests.get(f"{BASE_URL}/white-books/{book_id}/chapters")
        response.raise_for_status()
        chapters = response.json()
        print(f"✅ Retrieved {len(chapters)} chapters:")
        for ch in chapters:
            print(f"   - Chapter {ch['chapter_number']}: {ch['chapter_title']}")
    except Exception as e:
        print(f"❌ Get chapters failed: {e}")
    
    # 6. Get book with chapters
    print("\n6️⃣ Getting book with chapters...")
    try:
        response = requests.get(f"{BASE_URL}/white-books/{book_id}?include_chapters=true")
        response.raise_for_status()
        full_book = response.json()
        print(f"✅ Retrieved book:")
        print(f"   Title: {full_book['title']}")
        print(f"   Chapters: {len(full_book.get('chapters', []))}")
        print(f"   Views: {full_book['view_count']}")
        print(f"   Likes: {full_book['like_count']}")
    except Exception as e:
        print(f"❌ Get book failed: {e}")
    
    # 7. Update book metadata
    print("\n7️⃣ Updating book metadata...")
    update_data = {
        "description": "An updated description about my journey to wellness"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/white-books/{book_id}",
            json=update_data,
            headers=headers
        )
        response.raise_for_status()
        updated_book = response.json()
        print(f"✅ Updated book:")
        print(f"   New description: {updated_book['description']}")
    except Exception as e:
        print(f"❌ Update book failed: {e}")
    
    # 8. Publish book
    print("\n8️⃣ Publishing book...")
    try:
        response = requests.put(f"{BASE_URL}/white-books/{book_id}/publish", headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"✅ {result['message']}")
    except Exception as e:
        print(f"❌ Publish failed: {e}")
    
    # 9. Get published books
    print("\n9️⃣ Getting published books...")
    try:
        response = requests.get(f"{BASE_URL}/white-books/published")
        response.raise_for_status()
        published = response.json()
        print(f"✅ Found {len(published)} published books")
        for pb in published[:3]:  # Show first 3
            print(f"   - {pb['title']} by {pb.get('author_username', 'Unknown')}")
    except Exception as e:
        print(f"❌ Get published books failed: {e}")
    
    # 10. Search books
    print("\n🔟 Searching for 'healing'...")
    try:
        response = requests.get(f"{BASE_URL}/white-books/search/healing")
        response.raise_for_status()
        results = response.json()
        print(f"✅ Found {len(results)} matching books")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print(f"\n📚 Created book ID: {book_id}")
    print(f"   View it at: http://localhost:8000/care/white-books/{book_id}")

if __name__ == "__main__":
    test_white_books()
