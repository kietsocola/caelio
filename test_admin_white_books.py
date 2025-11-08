"""
Test Admin White Books API
Test các API quản lý white books cho admin
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/care"

def test_admin_white_books():
    """Test admin white books management"""
    
    print("=" * 60)
    print("TEST ADMIN WHITE BOOKS API")
    print("=" * 60)
    
    # 1. Login as admin
    print("\n1. Login as admin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@caelio.com",
            "password": "admin123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.text}")
        return
    
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin logged in successfully")
    
    # 2. Get all white books (no filter)
    print("\n2. Get all white books (no filter)...")
    response = requests.get(
        f"{BASE_URL}/admin/white-books",
        headers=admin_headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total books: {data['total']}")
        print(f"   Page: {data['page']}/{data['total_pages']}")
        print(f"   Books in page: {len(data['books'])}")
        if data['books']:
            print(f"   First book: {data['books'][0]['title']} (published: {data['books'][0]['is_published']})")
    else:
        print(f"❌ Error: {response.text}")
    
    # 3. Filter by published status
    print("\n3. Get only published books...")
    response = requests.get(
        f"{BASE_URL}/admin/white-books?is_published=true",
        headers=admin_headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Published books: {data['total']}")
    else:
        print(f"❌ Error: {response.text}")
    
    # 4. Filter by unpublished status
    print("\n4. Get only unpublished books...")
    response = requests.get(
        f"{BASE_URL}/admin/white-books?is_published=false",
        headers=admin_headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Unpublished books: {data['total']}")
        if data['books']:
            unpublished_book_id = data['books'][0]['id']
            print(f"   Sample book ID: {unpublished_book_id}")
            
            # Test admin publish
            print("\n5. Admin publish book...")
            response = requests.put(
                f"{BASE_URL}/admin/white-books/{unpublished_book_id}/publish",
                headers=admin_headers
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {response.json()['message']}")
                
                # Verify it's published
                response = requests.get(
                    f"{BASE_URL}/white-books/{unpublished_book_id}",
                    headers=admin_headers
                )
                if response.status_code == 200:
                    book = response.json()
                    print(f"   Verified: is_published = {book['is_published']}")
                
                # Test admin unpublish
                print("\n6. Admin unpublish book...")
                response = requests.put(
                    f"{BASE_URL}/admin/white-books/{unpublished_book_id}/unpublish",
                    headers=admin_headers
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ {response.json()['message']}")
                    
                    # Verify it's unpublished
                    response = requests.get(
                        f"{BASE_URL}/white-books/{unpublished_book_id}",
                        headers=admin_headers
                    )
                    if response.status_code == 200:
                        book = response.json()
                        print(f"   Verified: is_published = {book['is_published']}")
            else:
                print(f"❌ Error: {response.text}")
    else:
        print(f"❌ Error: {response.text}")
    
    # 7. Search by title
    print("\n7. Search books by title...")
    response = requests.get(
        f"{BASE_URL}/admin/white-books?title=book&page_size=5",
        headers=admin_headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} books matching 'book'")
        if data['books']:
            for book in data['books'][:3]:
                print(f"   - {book['title']} by {book['author_username']}")
    else:
        print(f"❌ Error: {response.text}")
    
    # 8. Filter by author
    print("\n8. Filter by author...")
    # Get first book's author_id
    response = requests.get(
        f"{BASE_URL}/admin/white-books?page_size=1",
        headers=admin_headers
    )
    if response.status_code == 200:
        data = response.json()
        if data['books']:
            author_id = data['books'][0]['author_id']
            print(f"Testing with author_id: {author_id}")
            
            response = requests.get(
                f"{BASE_URL}/admin/white-books?author_id={author_id}",
                headers=admin_headers
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Author has {data['total']} books")
                if data['books']:
                    print(f"   Author: {data['books'][0]['author_username']} ({data['books'][0]['author_email']})")
    
    # 9. Test regular user cannot access admin endpoints
    print("\n9. Test regular user cannot access admin endpoints...")
    # Create a test user
    import random
    test_email = f"testuser_{random.randint(1000, 9999)}@test.com"
    
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": "test123",
            "username": "testuser"
        }
    )
    
    if register_response.status_code == 200:
        user_token = register_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Try to access admin endpoint
        response = requests.get(
            f"{BASE_URL}/admin/white-books",
            headers=user_headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Regular user correctly blocked from admin endpoint")
        else:
            print(f"❌ Security issue: regular user got status {response.status_code}")
    
    # 10. Test user publish/unpublish their own book
    print("\n10. Test user can publish/unpublish their own book...")
    # Create a book as test user
    create_response = requests.post(
        f"{BASE_URL}/white-books/create",
        headers=user_headers,
        json={
            "title": "Test User Book",
            "description": "Testing user publish/unpublish",
            "tags": ["test"]
        }
    )
    
    if create_response.status_code == 200:
        user_book_id = create_response.json()["id"]
        print(f"Created book ID: {user_book_id}")
        
        # User publishes their own book
        response = requests.put(
            f"{BASE_URL}/white-books/{user_book_id}/publish",
            headers=user_headers
        )
        print(f"Publish status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()['message']}")
        
        # User unpublishes their own book
        response = requests.put(
            f"{BASE_URL}/white-books/{user_book_id}/unpublish",
            headers=user_headers
        )
        print(f"Unpublish status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()['message']}")
        
        # Clean up - delete the test book
        requests.delete(
            f"{BASE_URL}/white-books/{user_book_id}",
            headers=user_headers
        )
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_admin_white_books()
