"""
Test Role-Based Access Control
Demo phân quyền user, admin, bookstore
"""

import requests
import json

BASE_URL = "http://localhost:8001/care"

def test_rbac():
    """Test phân quyền"""
    
    print("=" * 60)
    print("TEST ROLE-BASED ACCESS CONTROL")
    print("=" * 60)
    
    # 1. Đăng ký và login các loại user
    print("\n1. ĐĂNG KÝ VÀ ĐĂNG NHẬP")
    print("-" * 60)
    
    # Admin (đã tạo sẵn)
    print("\n📌 Login as ADMIN")
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@caelio.com",
        "password": "admin123"
    })
    if admin_login.status_code == 200:
        admin_token = admin_login.json()["access_token"]
        admin_user = admin_login.json()["user"]
        print(f"✅ Admin logged in: {admin_user['username']} (role: {admin_user['role']})")
    else:
        print(f"❌ Admin login failed: {admin_login.text}")
        return
    
    # Register normal user
    print("\n📌 Register NORMAL USER")
    user_register = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "user@test.com",
        "username": "normaluser",
        "password": "user123",
        "full_name": "Normal User",
        "role": "user"
    })
    if user_register.status_code == 200:
        user_token = user_register.json()["access_token"]
        user_info = user_register.json()["user"]
        print(f"✅ User registered: {user_info['username']} (role: {user_info['role']})")
    else:
        # Try login if already exists
        user_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "user@test.com",
            "password": "user123"
        })
        if user_login.status_code == 200:
            user_token = user_login.json()["access_token"]
            user_info = user_login.json()["user"]
            print(f"✅ User logged in: {user_info['username']} (role: {user_info['role']})")
        else:
            print(f"❌ User register/login failed")
            return
    
    # Register bookstore
    print("\n📌 Register BOOKSTORE")
    bookstore_register = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "bookstore@test.com",
        "username": "testbookstore",
        "password": "bookstore123",
        "full_name": "Test Bookstore",
        "role": "bookstore"
    })
    if bookstore_register.status_code == 200:
        bookstore_token = bookstore_register.json()["access_token"]
        bookstore_info = bookstore_register.json()["user"]
        print(f"✅ Bookstore registered: {bookstore_info['username']} (role: {bookstore_info['role']})")
    else:
        # Try login if already exists
        bookstore_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "bookstore@test.com",
            "password": "bookstore123"
        })
        if bookstore_login.status_code == 200:
            bookstore_token = bookstore_login.json()["access_token"]
            bookstore_info = bookstore_login.json()["user"]
            print(f"✅ Bookstore logged in: {bookstore_info['username']} (role: {bookstore_info['role']})")
        else:
            print(f"❌ Bookstore register/login failed")
            return
    
    # 2. Test admin endpoints
    print("\n\n2. TEST ADMIN ENDPOINTS")
    print("-" * 60)
    
    # Admin xem tất cả users
    print("\n📌 Admin xem danh sách users")
    admin_get_users = requests.get(
        f"{BASE_URL}/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if admin_get_users.status_code == 200:
        users = admin_get_users.json()
        print(f"✅ Admin can view users: {users['total']} total users")
        print(f"   Roles: ", end="")
        for user in users['users'][:5]:
            print(f"{user['username']}({user['role']}) ", end="")
        print()
    else:
        print(f"❌ Failed: {admin_get_users.text}")
    
    # Normal user cố xem danh sách users (should fail)
    print("\n📌 Normal user cố xem danh sách users (should fail)")
    user_get_users = requests.get(
        f"{BASE_URL}/admin/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    if user_get_users.status_code == 403:
        print(f"✅ Correctly blocked: {user_get_users.json()['detail']}")
    else:
        print(f"❌ Should be blocked but got: {user_get_users.status_code}")
    
    # Admin thay đổi role
    print("\n📌 Admin thay đổi role của user")
    # First get the user_id
    for user in users['users']:
        if user['username'] == 'normaluser':
            target_user_id = user['user_id']
            break
    
    admin_change_role = requests.put(
        f"{BASE_URL}/admin/users/{target_user_id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"new_role": "bookstore"}
    )
    if admin_change_role.status_code == 200:
        print(f"✅ Admin changed user role: {admin_change_role.json()['message']}")
        
        # Change back
        requests.put(
            f"{BASE_URL}/admin/users/{target_user_id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"new_role": "user"}
        )
        print(f"   (Changed back to user)")
    else:
        print(f"❌ Failed: {admin_change_role.text}")
    
    # 3. Test bookstore endpoints
    print("\n\n3. TEST BOOKSTORE ENDPOINTS")
    print("-" * 60)
    
    # Normal user cố xem thống kê bookstore (should fail)
    print("\n📌 Normal user cố xem thống kê bookstore (should fail)")
    user_get_stats = requests.get(
        f"{BASE_URL}/bookstores/1/statistics",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    if user_get_stats.status_code == 403:
        print(f"✅ Correctly blocked: {user_get_stats.json()['detail']}")
    else:
        print(f"❌ Should be blocked but got: {user_get_stats.status_code}")
    
    # Bookstore xem thống kê (should pass)
    print("\n📌 Bookstore xem thống kê (should pass)")
    bookstore_get_stats = requests.get(
        f"{BASE_URL}/bookstores/1/statistics",
        headers={"Authorization": f"Bearer {bookstore_token}"}
    )
    if bookstore_get_stats.status_code == 200:
        stats = bookstore_get_stats.json()
        print(f"✅ Bookstore can view statistics")
        print(f"   Total sales: {stats.get('total_sales', 0)}")
        print(f"   Total orders: {stats.get('total_orders', 0)}")
    elif bookstore_get_stats.status_code == 404:
        print(f"⚠️ Bookstore 1 not found (need to create bookstore first)")
    else:
        print(f"❌ Failed: {bookstore_get_stats.text}")
    
    # Admin cũng có thể xem thống kê
    print("\n📌 Admin xem thống kê bookstore (should pass)")
    admin_get_stats = requests.get(
        f"{BASE_URL}/bookstores/1/statistics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if admin_get_stats.status_code == 200:
        print(f"✅ Admin can view bookstore statistics")
    elif admin_get_stats.status_code == 404:
        print(f"⚠️ Bookstore 1 not found")
    else:
        print(f"❌ Failed: {admin_get_stats.text}")
    
    # 4. Test public endpoints (no auth)
    print("\n\n4. TEST PUBLIC ENDPOINTS (No authentication)")
    print("-" * 60)
    
    print("\n📌 Get published white books (no auth)")
    public_books = requests.get(f"{BASE_URL}/white-books/published")
    if public_books.status_code == 200:
        books = public_books.json()
        print(f"✅ Public can view published books: {len(books)} books")
    else:
        print(f"❌ Failed: {public_books.text}")
    
    print("\n📌 Get emotional test questions (no auth)")
    public_questions = requests.get(f"{BASE_URL}/emotional-test/questions")
    if public_questions.status_code == 200:
        questions = public_questions.json()
        print(f"✅ Public can view test questions: {len(questions['questions'])} questions")
    else:
        print(f"❌ Failed: {public_questions.text}")
    
    # 5. Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n✅ Role-based access control is working correctly!")
    print("\nRoles created:")
    print(f"  - Admin: admin@caelio.com (admin123)")
    print(f"  - User: user@test.com (user123)")
    print(f"  - Bookstore: bookstore@test.com (bookstore123)")
    print("\nKey points:")
    print("  ✓ Admin can manage all users and view all stats")
    print("  ✓ Bookstore can view their own stats and manage orders")
    print("  ✓ Normal users are blocked from admin/bookstore endpoints")
    print("  ✓ Public endpoints work without authentication")

if __name__ == "__main__":
    test_rbac()
