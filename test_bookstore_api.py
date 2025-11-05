"""
Test script for Caelio Care Bookstore APIs
"""

import requests
import json

BASE_URL = "http://localhost:8000/care"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

"""
Test script for bookstore API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/care"

def print_response(title, response):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_bookstore_apis():
    """Test all bookstore-related APIs"""
    
    print("\n🚀 Testing Bookstore APIs")
    print("="*60)
    
    # 1. Register a bookstore
    print("\n1️⃣ Registering a bookstore...")
    bookstore_data = {
        "name": "Nhà Sách Fahasa",
        "email": "fahasa@example.com",
        "phone": "1900636467",
        "address": "60-62 Lê Lợi, Quận 1, TP.HCM",
        "latitude": 10.7720,
        "longitude": 106.6972,
        "commission_rate": 15.5,
        "description": "Chuỗi nhà sách lớn nhất Việt Nam",
        "website": "https://www.fahasa.com"
    }
    response = requests.post(f"{BASE_URL}/bookstores/register", json=bookstore_data)
    print_response("Register Bookstore", response)
    
    if response.status_code == 200:
        bookstore_id = response.json()['id']
        
        # 2. Get all bookstores
        print("\n2️⃣ Getting all bookstores...")
        response = requests.get(f"{BASE_URL}/bookstores")
        print_response("All Bookstores", response)
        
        # 3. Search for a book
        print("\n3️⃣ Searching for books...")
        response = requests.get(f"{BASE_URL}/books/search/Cây Cam")
        print_response("Search Books", response)
        
        if response.status_code == 200 and response.json()['books']:
            book_id = response.json()['books'][0]['product_id']
            
            # 4. Add book link
            print("\n4️⃣ Adding book purchase link...")
            link_data = {
                "book_id": book_id,
                "bookstore_id": bookstore_id,
                "purchase_url": f"https://www.fahasa.com/products/{book_id}",
                "price": 64800,
                "stock_status": "available"
            }
            response = requests.post(f"{BASE_URL}/bookstores/book-links", json=link_data)
            print_response("Add Book Link", response)
            
            # 5. Get book info
            print("\n5️⃣ Getting book info...")
            response = requests.get(f"{BASE_URL}/books/{book_id}")
            print_response("Book Info", response)
            
            # 6. Get purchase links (without GPS)
            print("\n6️⃣ Getting purchase links (without GPS)...")
            response = requests.get(f"{BASE_URL}/books/{book_id}/purchase-links")
            print_response("Purchase Links (No GPS)", response)
            
            # 7. Get purchase links (with GPS - near bookstore)
            print("\n7️⃣ Getting purchase links (with GPS)...")
            user_lat = 10.7723  # Near Fahasa
            user_lon = 106.6975
            response = requests.get(
                f"{BASE_URL}/books/{book_id}/purchase-links",
                params={"user_latitude": user_lat, "user_longitude": user_lon}
            )
            print_response("Purchase Links (With GPS)", response)
            
            # 8. Get bookstore books
            print("\n8️⃣ Getting books from bookstore...")
            response = requests.get(f"{BASE_URL}/bookstores/{bookstore_id}/books")
            print_response("Bookstore Books", response)
    
    # 9. Register second bookstore (different location)
    print("\n9️⃣ Registering another bookstore...")
    bookstore_data2 = {
        "name": "Nhà Sách Phương Nam",
        "email": "phuongnam@example.com",
        "phone": "02838225797",
        "address": "379 Nguyễn Thị Minh Khai, Quận 3, TP.HCM",
        "latitude": 10.7794,
        "longitude": 106.6889,
        "commission_rate": 18.0,
        "description": "Nhà sách Phương Nam - Tri thức và văn hóa",
        "website": "https://www.nhasachphuongnam.com"
    }
    response = requests.post(f"{BASE_URL}/bookstores/register", json=bookstore_data2)
    print_response("Register Second Bookstore", response)
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    print("Make sure Combined Caelio API is running on localhost:8000")
    print("Command: python run_api.py")
    input("Press Enter to start testing...")
    test_bookstore_apis()

    print("\n" + "="*60)
    print("🏪 TESTING BOOKSTORE APIs")
    print("="*60)
    
    # Test 1: Register first bookstore
    print("\n1️⃣  Register Bookstore - Fahasa")
    bookstore1 = {
        "name": "Nhà sách Fahasa",
        "email": "fahasa@example.com",
        "phone": "0901234567",
        "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
        "latitude": 10.7769,
        "longitude": 106.7009,
        "commission_rate": 15.5,
        "description": "Nhà sách lớn nhất Việt Nam",
        "website": "https://fahasa.com"
    }
    response = requests.post(f"{BASE_URL}/bookstores/register", json=bookstore1)
    print_response("Register Fahasa", response)
    
    # Test 2: Register second bookstore
    print("\n2️⃣  Register Bookstore - Tiki")
    bookstore2 = {
        "name": "Tiki",
        "email": "tiki@example.com",
        "phone": "0909876543",
        "address": "52 Út Tịch, Tân Bình, TP.HCM",
        "latitude": 10.8023,
        "longitude": 106.6504,
        "commission_rate": 12.0,
        "description": "Siêu thị trực tuyến",
        "website": "https://tiki.vn"
    }
    response = requests.post(f"{BASE_URL}/bookstores/register", json=bookstore2)
    print_response("Register Tiki", response)
    
    # Test 3: Register third bookstore
    print("\n3️⃣  Register Bookstore - Pibook")
    bookstore3 = {
        "name": "Pibook",
        "email": "pibook@example.com",
        "phone": "0912345678",
        "address": "456 Lê Lợi, Quận 1, TP.HCM",
        "latitude": 10.7750,
        "longitude": 106.7030,
        "commission_rate": 18.0,
        "description": "Nhà sách trẻ năng động",
        "website": "https://pibook.vn"
    }
    response = requests.post(f"{BASE_URL}/bookstores/register", json=bookstore3)
    print_response("Register Pibook", response)
    
    # Test 4: Get all bookstores
    print("\n4️⃣  Get All Bookstores")
    response = requests.get(f"{BASE_URL}/bookstores")
    print_response("All Bookstores", response)
    
    # Test 5: Get specific bookstore
    print("\n5️⃣  Get Bookstore Details (ID=1)")
    response = requests.get(f"{BASE_URL}/bookstores/1")
    print_response("Bookstore Details", response)
    
    # Test 6: Add book links
    print("\n6️⃣  Add Book Purchase Links")
    
    # Fahasa sells book 1
    link1 = {
        "book_id": 1,
        "bookstore_id": 1,
        "purchase_url": "https://fahasa.com/dac-nhan-tam",
        "price": 150000,
        "stock_status": "available"
    }
    response = requests.post(f"{BASE_URL}/bookstores/book-links", json=link1)
    print_response("Add Link: Fahasa - Book 1", response)
    
    # Tiki sells book 1
    link2 = {
        "book_id": 1,
        "bookstore_id": 2,
        "purchase_url": "https://tiki.vn/dac-nhan-tam",
        "price": 145000,
        "stock_status": "available"
    }
    response = requests.post(f"{BASE_URL}/bookstores/book-links", json=link2)
    print_response("Add Link: Tiki - Book 1", response)
    
    # Pibook sells book 1
    link3 = {
        "book_id": 1,
        "bookstore_id": 3,
        "purchase_url": "https://pibook.vn/dac-nhan-tam",
        "price": 148000,
        "stock_status": "available"
    }
    response = requests.post(f"{BASE_URL}/bookstores/book-links", json=link3)
    print_response("Add Link: Pibook - Book 1", response)
    
    # Test 7: Get purchase links WITHOUT GPS
    print("\n7️⃣  Get Purchase Links - WITHOUT GPS (sorted by commission only)")
    response = requests.get(f"{BASE_URL}/books/1/purchase-links")
    print_response("Purchase Links (No GPS)", response)
    
    # Test 8: Get purchase links WITH GPS (user near Fahasa)
    print("\n8️⃣  Get Purchase Links - WITH GPS (user at 10.7770, 106.7010 - near Fahasa)")
    response = requests.get(
        f"{BASE_URL}/books/1/purchase-links",
        params={
            "user_latitude": 10.7770,
            "user_longitude": 106.7010
        }
    )
    print_response("Purchase Links (With GPS - Near Fahasa)", response)
    
    # Test 9: Get purchase links WITH GPS (user near Tiki)
    print("\n9️⃣  Get Purchase Links - WITH GPS (user at 10.8020, 106.6500 - near Tiki)")
    response = requests.get(
        f"{BASE_URL}/books/1/purchase-links",
        params={
            "user_latitude": 10.8020,
            "user_longitude": 106.6500
        }
    )
    print_response("Purchase Links (With GPS - Near Tiki)", response)
    
    # Test 10: Get bookstore books
    print("\n🔟 Get Books from Fahasa")
    response = requests.get(f"{BASE_URL}/bookstores/1/books")
    print_response("Fahasa Books", response)
    
    print("\n" + "="*60)
    print("✅ BOOKSTORE API TESTING COMPLETED")
    print("="*60)

def test_integration_flow():
    """Test complete integration flow"""
    print("\n" + "="*60)
    print("🔄 TESTING COMPLETE INTEGRATION FLOW")
    print("="*60)
    
    # Step 1: Register user
    print("\n1️⃣  Register User")
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print_response("Register User", response)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Do emotional test
        print("\n2️⃣  Do Emotional Test")
        test_data = {
            "Q1": 4, "Q2": 3, "Q3": 5, "Q4": 2, "Q5": 4,
            "Q6": 3, "Q7": 2, "Q8": 4, "Q9": 3
        }
        response = requests.post(
            f"{BASE_URL}/emotional-test/analyze",
            json=test_data
        )
        print_response("Emotional Test Result", response)
        
        # Step 3: Get book prescription
        if response.status_code == 200:
            emotional_layer = response.json()["emotional_layer"]
            
            print(f"\n3️⃣  Get Book Prescription for '{emotional_layer}'")
            response = requests.get(
                f"{BASE_URL}/emotional-test/prescription/{emotional_layer}"
            )
            print_response("Book Prescription", response)
            
            # Step 4: Get purchase links for recommended books
            print("\n4️⃣  Get Purchase Links for Recommended Books (with GPS)")
            response = requests.get(
                f"{BASE_URL}/books/1/purchase-links",
                params={
                    "user_latitude": 10.7770,
                    "user_longitude": 106.7010
                }
            )
            print_response("Purchase Links", response)
    
    print("\n" + "="*60)
    print("✅ INTEGRATION FLOW TESTING COMPLETED")
    print("="*60)

if __name__ == "__main__":
    print("\n" + "🌟"*30)
    print("CAELIO CARE BOOKSTORE API TEST SUITE")
    print("🌟"*30)
    print("\n⚠️  Make sure the API server is running on localhost:8000")
    print("Command: python run_api.py\n")
    
    input("Press Enter to start testing...")
    
    # Test bookstore APIs
    test_bookstore_apis()
    
    print("\n")
    input("Press Enter to test integration flow...")
    
    # Test complete integration
    test_integration_flow()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
