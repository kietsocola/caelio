"""
Hệ thống phân loại tính cách đọc sách Caelio
Dựa trên tài liệu hướng dẫn chính thức
"""

class CaelioPersonalitySystem:
    def __init__(self):
        # 5 nhóm tính cách chính + 1 nhóm ẩn
        self.groups = {
            'Kết nối': 'The Connectors',  # Kết nối & Đồng cảm
            'Tự do': 'The Individuals',   # Tự do & Khẳng định  
            'Tri thức': 'The Thinkers',   # Tri thức & Chân lý
            'Chinh phục': 'The Achievers', # Ảnh hưởng & Chinh phục
            'Kiến tạo': 'The Builders'    # Thực tế & Kiến tạo
        }
        
        # Các lựa chọn kích hoạt điểm Synthesizer
        self.synthesizer_choices = ['C3E', 'C4C', 'C5C', 'C6E', 'C7E', 'C8C']
        
        # Câu hỏi hành trình KHÁM PHÁ (WHY + HOW)
        self.discovery_questions = {
            'Q1': {
                'question': 'Nếu một cuốn sách có linh hồn, linh hồn ấy nên làm gì cùng bạn?',
                'choices': {
                    'A': {'text': 'Cùng bạn đi qua những vùng cảm xúc sâu thẳm, để hiểu và được hiểu.', 'group': 'Kết nối'},
                    'B': {'text': 'Thức tỉnh trong bạn khát vọng tự do và bản sắc cá nhân.', 'group': 'Tự do'},
                    'C': {'text': 'Mở ra những bí mật ẩn sau tri thức của thế giới.', 'group': 'Tri thức'},
                    'D': {'text': 'Gieo trong bạn ngọn lửa chinh phục và thành tựu.', 'group': 'Chinh phục'},
                    'E': {'text': 'Dạy bạn cách xây một điều gì đó thực tế và bền vững.', 'group': 'Kiến tạo'}
                }
            },
            'Q2': {
                'question': 'Khi bạn chọn đọc, điều khiến bạn "ấn nút bắt đầu" là:',
                'choices': {
                    'A': {'text': 'Cảm xúc thôi thúc muốn đồng cảm với những người xa lạ.', 'group': 'Kết nối'},
                    'B': {'text': 'Niềm khao khát tự định nghĩa bản thân.', 'group': 'Tự do'},
                    'C': {'text': 'Sự tò mò muốn giải mã một bí ẩn lớn.', 'group': 'Tri thức'},
                    'D': {'text': 'Ham muốn tạo ra điều có giá trị trong thực tế.', 'group': 'Kiến tạo'},
                    'E': {'text': 'Mong muốn tiến gần hơn đến thành công.', 'group': 'Chinh phục'}
                }
            },
            'Q3': {
                'question': 'Khi đọc xong một cuốn sách tuyệt vời, bạn cảm thấy...',
                'choices': {
                    'A': {'text': 'Muốn chia sẻ và kết nối với ai đó.', 'group': 'Kết nối'},
                    'B': {'text': 'Muốn sáng tạo hoặc viết ra điều gì đó mới.', 'group': 'Tự do'},
                    'C': {'text': 'Muốn tiếp tục tìm hiểu sâu hơn, đi đến tận cùng.', 'group': 'Tri thức'},
                    'D': {'text': 'Muốn hành động và thử nghiệm ngay trong đời sống.', 'group': 'Chinh phục'},
                    'E': {'text': 'Muốn chiêm nghiệm, tổng hợp lại mọi điều trong đầu.', 'group': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q4': {
                'question': 'Khi cầm một cuốn sách, tâm trí bạn giống như:',
                'choices': {
                    'A': {'text': 'Một người thám hiểm muốn ghi nhớ từng chi tiết.', 'group': 'Tri thức', 'trait': 'Đọc sâu'},
                    'B': {'text': 'Một nhà du hành tự do lang thang qua nhiều vùng ý tưởng.', 'group': 'Tự do', 'trait': 'Đọc rộng'},
                    'C': {'text': 'Một người kết hợp cả hai: học sâu rồi liên kết rộng.', 'group': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q5': {
                'question': 'Trong một cuộc trò chuyện về sách, bạn thường:',
                'choices': {
                    'A': {'text': 'Lắng nghe câu chuyện và cảm xúc của người khác.', 'group': 'Kết nối', 'trait': 'Hướng ngoại'},
                    'B': {'text': 'Chia sẻ góc nhìn riêng biệt và tư tưởng của mình.', 'group': 'Tự do', 'trait': 'Hướng nội'},
                    'C': {'text': 'Phân tích, kết nối và làm rõ những luận điểm trái chiều.', 'group': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q6': {
                'question': 'Cảm giác lý tưởng của bạn khi đọc là:',
                'choices': {
                    'A': {'text': 'Bình yên, được hiểu.', 'group': 'Kết nối', 'trait': 'Agreeableness cao'},
                    'B': {'text': 'Tự do, bay bổng.', 'group': 'Tự do', 'trait': 'Openness cao'},
                    'C': {'text': 'Sâu thẳm, tập trung.', 'group': 'Tri thức', 'trait': 'Conscientiousness cao'},
                    'D': {'text': 'Hứng khởi, đầy năng lượng.', 'group': 'Chinh phục', 'trait': 'Extraversion cao'},
                    'E': {'text': 'Khám phá liên tục và "ghép các mảnh hình ảnh tri thức lại".', 'group': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q7': {
                'question': 'Một cuốn sách lý tưởng nên:',
                'choices': {
                    'A': {'text': 'Là lời tâm sự chân thành.', 'group': 'Kết nối'},
                    'B': {'text': 'Là tiếng gọi phiêu lưu.', 'group': 'Tự do'},
                    'C': {'text': 'Là cánh cửa tri thức.', 'group': 'Tri thức'},
                    'D': {'text': 'Là cẩm nang thành công.', 'group': 'Chinh phục'},
                    'E': {'text': 'Là tấm gương soi phản chiếu mọi điều bạn từng nghĩ.', 'group': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q8': {
                'question': 'Khi bạn đọc đến một ý tưởng khó hiểu, bạn:',
                'choices': {
                    'A': {'text': 'Bỏ qua và tiếp tục, vì cảm xúc là quan trọng nhất.', 'group': 'Kết nối'},
                    'B': {'text': 'Ghi chú lại để tìm hiểu sau.', 'group': 'Tri thức'},
                    'C': {'text': 'Truy tìm tất cả các nguồn liên quan, từ video, nghiên cứu, đến sách khác.', 'group': 'Synthesizer', 'synthesizer': True}
                }
            }
        }
        
        # Câu hỏi hành trình CHUYÊN NGÀNH
        self.professional_questions = {
            'Q1': {
                'question': 'Lĩnh vực bạn muốn đào sâu là gì?',
                'choices': {
                    'A': {'text': 'Kinh tế - Quản Trị - Tài chính', 'field': 'business'},
                    'B': {'text': 'Xã Hội - Nhân Văn', 'field': 'humanities'},
                    'C': {'text': 'Khoa học tự nhiên', 'field': 'science'},
                    'D': {'text': 'Công nghệ - Kỹ thuật', 'field': 'technology'},
                    'E': {'text': 'Y - Dược học', 'field': 'medical'},
                    'F': {'text': 'Sư phạm - Giáo dục', 'field': 'education'},
                    'G': {'text': 'Nghệ thuật - Thiết kế - Kiến trúc', 'field': 'arts'},
                    'H': {'text': 'Nông - Lâm - Ngư nghiệp', 'field': 'agriculture'}
                }
            },
            'Q2': {
                'question': 'Mục tiêu đọc của bạn là:',
                'choices': {
                    'A': {'text': 'Xây nền tảng lý thuyết vững chắc.', 'motivation': 'foundational'},
                    'B': {'text': 'Giải quyết vấn đề thực tế trong công việc.', 'motivation': 'practical'},
                    'C': {'text': 'Mở rộng tư duy và khám phá tri thức mới.', 'motivation': 'exploratory'}
                }
            },
            'Q3': {
                'question': 'Khi học một vấn đề mới, bạn thích:',
                'choices': {
                    'A': {'text': 'Có lộ trình rõ ràng, từ cơ bản đến nâng cao.', 'style': 'structured'},
                    'B': {'text': 'Tự mình tìm các liên kết giữa các lĩnh vực.', 'style': 'integrative', 'synthesizer_potential': True}
                }
            },
            'Q4': {
                'question': 'Cách trình bày bạn thấy hấp dẫn nhất:',
                'choices': {
                    'A': {'text': 'Sách học chuyên sâu, chặt chẽ, có trích dẫn.', 'presentation': 'analytical'},
                    'B': {'text': 'Sách kể chuyện sinh động, dễ hiểu.', 'presentation': 'narrative'},
                    'C': {'text': 'Sách có khả năng kết nối lý thuyết với góc nhìn đa ngành.', 'presentation': 'integrative', 'synthesizer': True}
                }
            }
        }

    def calculate_discovery_profile(self, answers):
        """Tính toán profile cho hành trình KHÁM PHÁ"""
        scores = {group: 0 for group in self.groups.keys()}
        synthesizer_score = 0
        
        # Tính điểm cho từng nhóm
        for q_id, choice in answers.items():
            question = self.discovery_questions[q_id]
            choice_data = question['choices'][choice]
            
            # Điểm cho nhóm chính
            if choice_data['group'] in scores:
                scores[choice_data['group']] += 1
            
            # Điểm Synthesizer
            if choice_data.get('synthesizer', False):
                synthesizer_score += 1
        
        return self._determine_profile(scores, synthesizer_score, answers)
    
    def calculate_professional_profile(self, discovery_answers, professional_answers):
        """Tính toán profile cho hành trình CHUYÊN NGÀNH"""
        # Lấy profile từ hành trình khám phá
        base_profile = self.calculate_discovery_profile(discovery_answers)
        
        # Thêm thông tin chuyên ngành
        field = self.professional_questions['Q1']['choices'][professional_answers['Q1']]['field']
        motivation = self.professional_questions['Q2']['choices'][professional_answers['Q2']]['motivation'] 
        style = self.professional_questions['Q3']['choices'][professional_answers['Q3']]['style']
        presentation = self.professional_questions['Q4']['choices'][professional_answers['Q4']]['presentation']
        
        # Kiểm tra Synthesizer tiềm năng trong chuyên ngành
        synthesizer_indicators = 0
        if professional_answers['Q3'] == 'B':  # Tự mình tìm liên kết
            synthesizer_indicators += 1
        if professional_answers['Q4'] == 'C':  # Kết nối đa ngành
            synthesizer_indicators += 1
            
        professional_profile = {
            **base_profile,
            'field': field,
            'motivation': motivation,
            'learning_style': style,
            'presentation_preference': presentation,
            'professional_synthesizer_indicators': synthesizer_indicators
        }
        
        return professional_profile
    
    def _determine_profile(self, scores, synthesizer_score, answers):
        """Xác định profile dựa trên điểm số"""
        # Sắp xếp theo điểm số
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_group = sorted_scores[0][0]
        primary_score = sorted_scores[0][1]
        
        secondary_group = sorted_scores[1][0] if len(sorted_scores) > 1 else None
        secondary_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        # Kiểm tra nếu có tie trong nhóm chính
        if secondary_score == primary_score:
            # Ưu tiên nhóm xuất hiện nhiều trong WHY (Q1-Q3)
            why_answers = {q: answers[q] for q in ['Q1', 'Q2', 'Q3'] if q in answers}
            why_groups = []
            for q_id, choice in why_answers.items():
                if q_id in self.discovery_questions:
                    group = self.discovery_questions[q_id]['choices'][choice]['group']
                    if group in self.groups:
                        why_groups.append(group)
            
            # Đếm tần suất trong phần WHY
            why_counts = {group: why_groups.count(group) for group in [primary_group, secondary_group]}
            if why_counts[secondary_group] > why_counts[primary_group]:
                primary_group, secondary_group = secondary_group, primary_group
                primary_score, secondary_score = secondary_score, primary_score
        
        # Kiểm tra điều kiện Synthesizer
        is_synthesizer = False
        if synthesizer_score >= 3 and abs(primary_score - secondary_score) <= 1:
            is_synthesizer = True
        
        # Tạo profile name
        profile_name = primary_group
        if is_synthesizer:
            profile_name += "–Synthesizer"
        
        return {
            'primary_group': primary_group,
            'secondary_group': secondary_group,
            'primary_score': primary_score,
            'secondary_score': secondary_score,
            'synthesizer_score': synthesizer_score,
            'is_synthesizer': is_synthesizer,
            'profile_name': profile_name,
            'english_name': self.groups[primary_group] + ("–Synthesizer" if is_synthesizer else ""),
            'all_scores': scores,
            'is_multi_motivated': abs(primary_score - secondary_score) <= 1
        }

    def get_book_recommendations(self, profile):
        """Đưa ra gợi ý sách dựa trên profile"""
        recommendations = {
            'Kết nối': {
                'base': ['Tâm lý tình cảm', 'chữa lành', 'tản văn', 'tiểu thuyết gia đình'],
                'synthesizer': ['sách phản tư về tình người', 'triết học nhân văn', 'sách về đồng cảm sâu sắc']
            },
            'Tự do': {
                'base': ['Du ký', 'nghệ thuật sống', 'tiểu thuyết sáng tạo', 'sách phản tư xã hội'],
                'synthesizer': ['triết học về tự do', 'sách về tư duy độc lập', 'phản biện xã hội sâu sắc']
            },
            'Tri thức': {
                'base': ['Khoa học phổ thông', 'triết học', 'lịch sử', 'sách phân tích chuyên sâu'],
                'synthesizer': ['sách liên ngành', 'hệ thống tư duy', 'triết học khoa học']
            },
            'Chinh phục': {
                'base': ['Sách truyền cảm hứng', 'lãnh đạo', 'chiến lược', 'hồi ký thành công'],
                'synthesizer': ['sách phản tư về thành công', 'lý thuyết lãnh đạo', 'case study phức tạp']
            },
            'Kiến tạo': {
                'base': ['Sách kỹ năng', 'tài chính', 'marketing', 'khởi nghiệp', 'sách hướng nghiệp'],
                'synthesizer': ['sách kết hợp lý thuyết-thực hành', 'tư duy hệ thống kinh doanh']
            }
        }
        
        primary = profile['primary_group']
        if profile['is_synthesizer']:
            return recommendations[primary]['synthesizer']
        else:
            return recommendations[primary]['base']

# Test functions
def run_discovery_test():
    """Test hành trình khám phá"""
    system = CaelioPersonalitySystem()
    
    print("=== HÀNH TRÌNH KHÁM PHÁ ===")
    print("Khi đến với Caelio, bạn đang tìm kiếm điều gì?")
    print("A. Một cuốn sách khiến tôi nhìn thấy chính mình theo một cách mới. ➡ Dành cho hành trình khám phá.")
    print("B. Một cuốn sách giúp tôi học, làm việc hoặc nghiên cứu hiệu quả hơn. ➡ Dành cho hành trình chuyên ngành.")
    
    choice = input("\nChọn A hoặc B: ").upper().strip()
    
    if choice == 'A':
        # Chạy hành trình khám phá
        answers = {}
        
        for q_id, question_data in system.discovery_questions.items():
            print(f"\n{q_id}. {question_data['question']}")
            for choice_key, choice_data in question_data['choices'].items():
                print(f"{choice_key}. {choice_data['text']}")
            
            user_choice = input("Chọn: ").upper().strip()
            while user_choice not in question_data['choices']:
                user_choice = input("Vui lòng chọn lại: ").upper().strip()
            answers[q_id] = user_choice
        
        # Tính toán kết quả
        profile = system.calculate_discovery_profile(answers)
        
        print(f"\n=== KẾT QUẢ ===")
        print(f"Profile: {profile['profile_name']}")
        print(f"English: {profile['english_name']}")
        print(f"Nhóm chính: {profile['primary_group']} ({profile['primary_score']} điểm)")
        if profile['secondary_group']:
            print(f"Nhóm phụ: {profile['secondary_group']} ({profile['secondary_score']} điểm)")
        print(f"Điểm Synthesizer: {profile['synthesizer_score']}")
        print(f"Là Synthesizer: {profile['is_synthesizer']}")
        print(f"Đa động lực: {profile['is_multi_motivated']}")
        
        # Gợi ý sách
        recommendations = system.get_book_recommendations(profile)
        print(f"\nGợi ý sách: {', '.join(recommendations)}")
        
        return profile
    
    elif choice == 'B':
        print("\n=== HÀNH TRÌNH CHUYÊN NGÀNH ===")
        print("Chức năng này sẽ được implement sau.")
        return None
    
    else:
        print("Lựa chọn không hợp lệ!")
        return None

def run_example_test():
    """Chạy ví dụ test theo tài liệu"""
    system = CaelioPersonalitySystem()
    
    # Ví dụ từ tài liệu
    example_answers = {
        'Q1': 'C',  # Tri thức
        'Q2': 'D',  # Kiến tạo  
        'Q3': 'E',  # Synthesizer +1
        'Q4': 'C',  # Synthesizer +1
        'Q5': 'B',  # Tự do
        'Q6': 'E',  # Synthesizer +1
        'Q7': 'C',  # Tri thức
        'Q8': 'C'   # Synthesizer +1
    }
    
    profile = system.calculate_discovery_profile(example_answers)
    
    print("=== VÍ DỤ KIỂM TRA ===")
    print("Câu trả lời:", example_answers)
    print(f"Profile: {profile['profile_name']}")
    print("Kết quả mong đợi: Thinker–Synthesizer")
    print("Đúng không?", "✓" if "Tri thức" in profile['profile_name'] and "Synthesizer" in profile['profile_name'] else "✗")

if __name__ == "__main__":
    # Chạy ví dụ kiểm tra trước
    run_example_test()
    
    print("\n" + "="*50)
    
    # Chạy test tương tác
    run_discovery_test()