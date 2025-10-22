"""
Tích hợp hệ thống Caelio với dữ liệu sách
Mapping từ 5 nhóm tính cách + Synthesizer sang categories sách
"""

import pandas as pd
from caelio_personality_system import CaelioPersonalitySystem

class CaelioBookMatcher:
    def __init__(self):
        self.personality_system = CaelioPersonalitySystem()
        
        # Mapping từ nhóm tính cách sang book categories
        self.personality_to_categories = {
            'Kết nối': {
                'base': [
                    'Sách tư duy - Kỹ năng sống',
                    'Tâm lý - Giáo dục giới tính', 
                    'Gia đình',
                    'Nuôi dạy con',
                    'Tình yêu - Hôn nhân',
                    'Xã hội',
                    'Văn hóa - Xã hội',
                    'Tâm lý học',
                    'Giao tiếp',
                    'Tiểu thuyết tình cảm',
                    'Truyện ngắn - Tản văn'
                ],
                'synthesizer': [
                    'Triết học',
                    'Tôn giáo',
                    'Tâm lý học sâu',
                    'Văn học phản tư',
                    'Khoa học xã hội'
                ]
            },
            
            'Tự do': {
                'base': [
                    'Du lịch',
                    'Ẩm thực', 
                    'Nấu ăn',
                    'Sở thích',
                    'Thể thao - Giải trí',
                    'Nuôi trồng',
                    'Làm vườn',
                    'Thiền',
                    'Yoga',
                    'Nghệ thuật sống',
                    'Phong cách sống'
                ],
                'synthesizer': [
                    'Triết học về tự do',
                    'Nghệ thuật',
                    'Văn học hiện đại',
                    'Tư tưởng độc lập'
                ]
            },
            
            'Tri thức': {
                'base': [
                    'Khoa học - Kỹ thuật',
                    'Lịch sử', 
                    'Địa lý',
                    'Chính trị - Pháp luật',
                    'Sách Học Tiếng Anh',
                    'Sách giáo khoa',
                    'Sách chuyên ngành',
                    'Từ điển',
                    'Sách tham khảo',
                    'Khoa học phổ thông'
                ],
                'synthesizer': [
                    'Triết học khoa học',
                    'Lịch sử tư tưởng',
                    'Khoa học liên ngành',
                    'Tư duy hệ thống'
                ]
            },
            
            'Chinh phục': {
                'base': [
                    'Bài học kinh doanh',
                    'Sách Marketing - Bán hàng',
                    'Sách kỹ năng làm việc', 
                    'Quản trị - Lãnh đạo',
                    'Khởi nghiệp',
                    'Tài chính - Kế toán',
                    'Chứng khoán - Đầu tư',
                    'Bất động sản',
                    'Thể thao',
                    'Bóng đá',
                    'Truyền cảm hứng'
                ],
                'synthesizer': [
                    'Chiến lược cấp cao',
                    'Lý thuyết quản trị',
                    'Case study phức tạp',
                    'Tư duy chiến lược'
                ]
            },
            
            'Kiến tạo': {
                'base': [
                    'Tiểu Thuyết',
                    'Truyện ngắn - Tản văn - Tạp Văn',
                    'Thơ ca',
                    'Tác phẩm kinh điển', 
                    'Văn học',
                    'Nghệ thuật',
                    'Sách nghệ thuật sống đẹp',
                    'Âm nhạc',
                    'Hội họa',
                    'Nhiếp ảnh',
                    'Thời trang',
                    'Làm đẹp',
                    'Kiến trúc',
                    'Thiết kế'
                ],
                'synthesizer': [
                    'Nghệ thuật đương đại',
                    'Lý thuyết sáng tạo',
                    'Văn học hiện đại',
                    'Triết học nghệ thuật'
                ]
            }
        }
    
    def map_personality_to_books(self, profile, book_df):
        """
        Lọc sách phù hợp dựa trên personality profile
        """
        primary_group = profile['primary_group']
        is_synthesizer = profile['is_synthesizer']
        
        # Lấy danh sách categories phù hợp
        if is_synthesizer:
            target_categories = (
                self.personality_to_categories[primary_group]['base'] +
                self.personality_to_categories[primary_group]['synthesizer']
            )
        else:
            target_categories = self.personality_to_categories[primary_group]['base']
        
        # Lọc sách theo categories
        matched_books = book_df[
            book_df['category'].isin(target_categories)
        ].copy()
        
        # Thêm matching score
        matched_books['personality_match_score'] = matched_books['category'].apply(
            lambda cat: self._calculate_match_score(cat, primary_group, is_synthesizer)
        )
        
        # Sắp xếp theo độ phù hợp
        matched_books = matched_books.sort_values('personality_match_score', ascending=False)
        
        return matched_books
    
    def _calculate_match_score(self, category, primary_group, is_synthesizer):
        """Tính điểm phù hợp cho category"""
        base_categories = self.personality_to_categories[primary_group]['base']
        synth_categories = self.personality_to_categories[primary_group]['synthesizer']
        
        if category in synth_categories and is_synthesizer:
            return 1.0  # Perfect match cho Synthesizer
        elif category in base_categories:
            return 0.8  # Good match cho base
        elif category in synth_categories:
            return 0.6  # OK match cho Synthesizer categories nhưng không phải Synthesizer
        else:
            return 0.2  # Low match
    
    def get_personalized_recommendations(self, answers, book_df, top_n=20):
        """
        Đưa ra gợi ý sách cá nhân hóa
        """
        # Tính personality profile
        profile = self.personality_system.calculate_discovery_profile(answers)
        
        # Lọc sách phù hợp
        matched_books = self.map_personality_to_books(profile, book_df)
        
        # Lấy top N sách
        top_recommendations = matched_books.head(top_n)
        
        return {
            'profile': profile,
            'recommendations': top_recommendations,
            'total_matches': len(matched_books),
            'match_distribution': matched_books.groupby('category').size().to_dict()
        }
    
    def analyze_book_compatibility(self, book_df):
        """
        Phân tích độ tương thích của từng sách với các nhóm tính cách
        """
        results = []
        
        for _, book in book_df.iterrows():
            book_analysis = {
                'product_id': book['product_id'],
                'title': book['title'],
                'category': book['category'],
                'compatibility': {}
            }
            
            # Kiểm tra độ tương thích với từng nhóm
            for group in self.personality_to_categories.keys():
                base_score = 0.8 if book['category'] in self.personality_to_categories[group]['base'] else 0
                synth_score = 1.0 if book['category'] in self.personality_to_categories[group]['synthesizer'] else 0
                
                book_analysis['compatibility'][group] = {
                    'base_match': base_score > 0,
                    'synthesizer_match': synth_score > 0,
                    'max_score': max(base_score, synth_score)
                }
            
            # Tìm nhóm phù hợp nhất
            best_group = max(
                book_analysis['compatibility'].items(), 
                key=lambda x: x[1]['max_score']
            )
            
            book_analysis['best_match_group'] = best_group[0]
            book_analysis['best_match_score'] = best_group[1]['max_score']
            
            results.append(book_analysis)
        
        return results

def demo_personality_matching():
    """Demo hệ thống matching"""
    # Khởi tạo
    matcher = CaelioBookMatcher()
    
    # Load dữ liệu sách (giả sử có file CSV)
    try:
        book_df = pd.read_csv('dataset/books_full_data.csv')
        print(f"📚 Loaded {len(book_df)} books")
    except:
        # Tạo dữ liệu mẫu nếu không có file
        sample_books = [
            {'product_id': 1, 'title': 'Cây Cam Ngọt Của Tôi', 'category': 'Tiểu Thuyết'},
            {'product_id': 2, 'title': 'Thao Túng Tâm Lý', 'category': 'Sách tư duy - Kỹ năng sống'},
            {'product_id': 3, 'title': 'Nhà Giả Kim', 'category': 'Tác phẩm kinh điển'},
            {'product_id': 4, 'title': 'Marketing 4.0', 'category': 'Sách Marketing - Bán hàng'},
            {'product_id': 5, 'title': 'Lịch Sử Thế Giới', 'category': 'Lịch sử'},
        ]
        book_df = pd.DataFrame(sample_books)
        print(f"📚 Using {len(book_df)} sample books")
    
    # Test với profile mẫu
    test_answers = {
        'Q1': 'A',  # Kết nối
        'Q2': 'A',  # Kết nối  
        'Q3': 'A',  # Kết nối
        'Q4': 'A',  # Tri thức (đọc sâu)
        'Q5': 'A',  # Kết nối
        'Q6': 'A',  # Kết nối
        'Q7': 'A',  # Kết nối
        'Q8': 'A'   # Kết nối
    }
    
    # Tính toán gợi ý
    result = matcher.get_personalized_recommendations(test_answers, book_df)
    
    print(f"\n=== KẾT QUẢ PHÂN TÍCH ===")
    print(f"Profile: {result['profile']['profile_name']}")
    print(f"Tổng sách phù hợp: {result['total_matches']}")
    print(f"\nTop recommendations:")
    
    if len(result['recommendations']) > 0:
        for _, book in result['recommendations'].head(5).iterrows():
            print(f"- {book['title']} ({book['category']}) - Score: {book['personality_match_score']:.2f}")
    else:
        print("Không có sách phù hợp trong dataset mẫu")
    
    return result

def create_personality_labeled_dataset():
    """
    Tạo dataset với personality labels cho tất cả sách
    """
    matcher = CaelioBookMatcher()
    
    try:
        # Load dataset
        book_df = pd.read_csv('dataset/books_full_data.csv')
        print(f"📚 Processing {len(book_df)} books...")
        
        # Phân tích compatibility
        compatibility_results = matcher.analyze_book_compatibility(book_df)
        
        # Chuyển thành DataFrame
        compatibility_df = pd.DataFrame([
            {
                'product_id': result['product_id'],
                'title': result['title'], 
                'category': result['category'],
                'best_personality_match': result['best_match_group'],
                'match_score': result['best_match_score'],
                'ket_noi_match': result['compatibility']['Kết nối']['max_score'],
                'tu_do_match': result['compatibility']['Tự do']['max_score'],
                'tri_thuc_match': result['compatibility']['Tri thức']['max_score'],
                'chinh_phuc_match': result['compatibility']['Chinh phục']['max_score'],
                'kien_tao_match': result['compatibility']['Kiến tạo']['max_score']
            }
            for result in compatibility_results
        ])
        
        # Merge với dữ liệu gốc
        final_df = book_df.merge(compatibility_df, on='product_id', how='left')
        
        # Lưu file
        output_file = 'dataset/books_with_personality_labels.csv'
        final_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Saved to: {output_file}")
        
        # Thống kê
        print(f"\n📊 Personality distribution:")
        print(compatibility_df['best_personality_match'].value_counts())
        
        return final_df
        
    except FileNotFoundError:
        print("❌ File dataset/books_full_data.csv not found")
        return None

if __name__ == "__main__":
    print("=== CAELIO BOOK MATCHING SYSTEM ===")
    
    # Demo
    demo_personality_matching()
    
    print("\n" + "="*50)
    
    # Tạo dataset với personality labels
    create_personality_labeled_dataset()