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
        
        # Câu hỏi hành trình KHÁM PHÁ - 10 câu theo guide_11_11.md
        # Q1-Q4 (WHY): Động cơ đọc sách
        # Q5-Q10 (HOW): Phong cách đọc + Big Five
        self.discovery_questions = {
            # WHY Section - Câu 1-4
            'Q1': {
                'question': 'Nếu một cuốn sách có linh hồn, linh hồn ấy nên làm gì cùng bạn?',
                'section': 'WHY',
                'choices': {
                    'A': {'text': 'Cùng bạn đi qua những vùng cảm xúc sâu thẳm, để thấu hiểu các mối quan hệ gia đình và xã hội.', 'group': 'Kết nối'},
                    'B': {'text': 'Thức tỉnh trong bạn khát vọng tự do, tìm ra bản sắc cá nhân nhưng vẫn hài hòa với thế giới.', 'group': 'Tự do'},
                    'C': {'text': 'Mở ra những bí mật, giúp bạn hiểu rõ bản chất và quy luật của thế giới.', 'group': 'Tri thức'},
                    'D': {'text': 'Gieo trong bạn ngọn lửa chinh phục, tạo ra giá trị và tầm ảnh hưởng cho tập thể.', 'group': 'Chinh phục'},
                    'E': {'text': 'Dạy bạn cách xây một điều gì đó thực tế và bền vững cho tương lai.', 'group': 'Kiến tạo'}
                }
            },
            'Q2': {
                'question': 'Điều khiến bạn "ấn nút bắt đầu" đọc một cuốn sách là:',
                'section': 'WHY',
                'choices': {
                    'A': {'text': 'Cảm xúc thôi thúc muốn đồng cảm với một phận người, một câu chuyện nhân văn.', 'group': 'Kết nối'},
                    'B': {'text': 'Niềm khao khát được "xách ba lô lên và đi", tự định nghĩa bản thân.', 'group': 'Tự do'},
                    'C': {'text': 'Sự tò mò muốn giải mã một bí ẩn hoặc hệ thống tri thức.', 'group': 'Tri thức'},
                    'D': {'text': 'Mong muốn kiên trì học hỏi để tiến gần hơn đến thành công.', 'group': 'Chinh phục'},
                    'E': {'text': 'Ham muốn tạo ra một ý tưởng, một kế hoạch, một sản phẩm.', 'group': 'Kiến tạo'}
                }
            },
            'Q3': {
                'question': 'Mục đích lớn nhất của bạn khi đọc sách là gì?',
                'section': 'WHY',
                'choices': {
                    'A': {'text': 'Để thấu hiểu con người, học cách đối nhân xử thế và chữa lành cảm xúc.', 'group': 'Kết nối'},
                    'B': {'text': 'Để tìm ra con đường riêng, sống tự do và đúng với bản sắc của mình.', 'group': 'Tự do'},
                    'C': {'text': 'Để giải mã thế giới, hiểu sâu về một lĩnh vực.', 'group': 'Tri thức'},
                    'D': {'text': 'Để có động lực, học hỏi kỹ năng và đạt được thành tựu.', 'group': 'Chinh phục'},
                    'E': {'text': 'Để có cảm hứng, tạo ra một sản phẩm hoặc ý tưởng mới.', 'group': 'Kiến tạo'}
                }
            },
            'Q4': {
                'question': 'Một cuốn sách lý tưởng nên:',
                'section': 'WHY',
                'choices': {
                    'A': {'text': 'Là lời tâm sự chân thành, giàu tình người.', 'group': 'Kết nối'},
                    'B': {'text': 'Là tiếng gọi phiêu lưu.', 'group': 'Tự do'},
                    'C': {'text': 'Là cánh cửa tri thức.', 'group': 'Tri thức'},
                    'D': {'text': 'Là cẩm nang thành công.', 'group': 'Chinh phục'},
                    'E': {'text': 'Là bản thiết kế để sáng tạo và xây dựng.', 'group': 'Kiến tạo'}
                }
            },
            
            # HOW Section - Câu 5-10
            'Q5': {
                'question': 'Khi cầm một cuốn sách, tâm trí bạn giống như:',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Một người thám hiểm, muốn đi sâu, đào bới, và ghi nhớ từng chi tiết.', 'trait': 'Deep', 'bigfive': 'Conscientiousness High'},
                    'B': {'text': 'Một nhà du hành, lướt qua nhiều vùng ý tưởng để tìm cảm hứng mới.', 'trait': 'Wide', 'bigfive': 'Openness High'},
                    'C': {'text': 'Một nhà tổng hợp, vừa đào sâu vừa liên kết rộng để tạo ra bức tranh lớn.', 'trait': 'Synthesizer', 'synthesizer': True}
                }
            },
            'Q6': {
                'question': 'Bạn tin tưởng vào nguồn kiến thức nào hơn?',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Sách được viết bởi chuyên gia, học giả, người có thẩm quyền hoặc đã được kiểm chứng (kinh điển).', 'trait': 'Academic', 'bigfive': 'High Power Distance'},
                    'B': {'text': 'Sách được viết bởi người trẻ, người có trải nghiệm thực tế, hoặc được cộng đồng/KOLs đánh giá cao.', 'trait': 'Practical', 'bigfive': 'Low Power Distance'}
                }
            },
            'Q7': {
                'question': 'Cuốn sách lý tưởng để "sạc" lại năng lượng cho bạn là:',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Một cuốn sách truyền cảm hứng, thúc đẩy hành động, đầy khí thế.', 'trait': 'Social', 'bigfive': 'Extraversion High'},
                    'B': {'text': 'Một cuốn sách yên tĩnh, nội tâm, suy tư sâu lắng.', 'trait': 'Reflective', 'bigfive': 'Introversion'}
                }
            },
            'Q8': {
                'question': 'Bạn bị cuốn hút hơn bởi kiểu nhân vật nào?',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Nhân vật có lòng trắc ẩn, biết hy sinh vì gia đình/cộng đồng, làm điều đúng đắn.', 'trait': 'Empathic', 'bigfive': 'Agreeableness High'},
                    'B': {'text': 'Nhân vật phức tạp, gai góc, dám phá vỡ quy tắc để theo đuổi mục tiêu cá nhân.', 'trait': 'Analytical', 'bigfive': 'Agreeableness Low'}
                }
            },
            'Q9': {
                'question': 'Khi chọn sách để thư giãn cuối ngày, bạn tìm kiếm:',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Cảm giác an toàn, dễ chịu, một thế giới "chữa lành" để trốn vào.', 'trait': 'Light', 'bigfive': 'Neuroticism High'},
                    'B': {'text': 'Cảm giác kịch tính, hồi hộp, gay cấn, thậm chí là sợ hãi.', 'trait': 'Intense', 'bigfive': 'Neuroticism Low'}
                }
            },
            'Q10': {
                'question': 'Bạn thích cách trình bày sách như thế nào nhất?',
                'section': 'HOW',
                'choices': {
                    'A': {'text': 'Kể chuyện sinh động, giàu cảm xúc, dùng ví dụ đời thường.', 'trait': 'Emotional', 'bigfive': 'Agreeableness High'},
                    'B': {'text': 'Có cấu trúc, logic chặt chẽ, từng bước, có trích dẫn.', 'trait': 'Structured', 'bigfive': 'Conscientiousness High'},
                    'C': {'text': 'Kích thích tư duy, kết nối đa ngành, mang tính triết lý và phản tư.', 'trait': 'Synthesizer', 'synthesizer': True}
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
        """
        Tính toán profile cho hành trình KHÁM PHÁ - 10 câu theo guide_11_11.md
        
        WHY (Q1-Q4): Đo động cơ đọc → Archetype
        - Mỗi câu trả lời cộng 1 điểm cho archetype tương ứng
        - P_archetype_i = WHY_i / ΣWHY
        - Archetype có điểm cao nhất = nhóm chính
        
        HOW (Q5-Q10): Đo phong cách đọc → Big Five + Style traits
        - Thu thập style traits (Deep, Wide, Synthesizer, etc.)
        - P_how_j = HOW_j / ΣHOW
        
        Synthesizer Flag: ≥3 indicators = TRUE
        """
        # Khởi tạo counters
        archetype_scores = {group: 0 for group in self.groups.keys()}
        synthesizer_score = 0
        style_traits = []
        
        # Process WHY section (Q1-Q4): Động cơ đọc
        for q_id in ['Q1', 'Q2', 'Q3', 'Q4']:
            if q_id in answers:
                choice = answers[q_id]
                question = self.discovery_questions.get(q_id)
                if question:
                    choice_data = question['choices'].get(choice, {})
                    
                    # Count archetype score
                    group = choice_data.get('group')
                    if group and group in archetype_scores:
                        archetype_scores[group] += 1
        
        # Process HOW section (Q5-Q10): Phong cách đọc
        for q_id in ['Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']:
            if q_id in answers:
                choice = answers[q_id]
                question = self.discovery_questions.get(q_id)
                if question:
                    choice_data = question['choices'].get(choice, {})
                    
                    # Collect style traits
                    trait = choice_data.get('trait')
                    if trait:
                        style_traits.append(trait)
                    
                    # Check synthesizer indicator
                    if choice_data.get('synthesizer', False):
                        synthesizer_score += 1
        
        return self._determine_profile(archetype_scores, synthesizer_score, style_traits, answers)
    
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
    
    def _determine_profile(self, archetype_scores, synthesizer_score, style_traits, answers):
        """
        Xác định profile dựa trên điểm số theo guide_11_11.md
        
        Logic:
        - WHY (60%): Archetype có điểm cao nhất = nhóm chính
        - Nếu tie, ưu tiên Q1 (câu quan trọng nhất)
        - Synthesizer flag: ≥3 indicators
        - HOW (40%): Style traits từ Q5-Q10
        """
        # Sắp xếp archetypes theo điểm số
        sorted_scores = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
        primary_group = sorted_scores[0][0]
        primary_score = sorted_scores[0][1]
        
        secondary_group = sorted_scores[1][0] if len(sorted_scores) > 1 else None
        secondary_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        # Kiểm tra nếu có tie trong archetype chính
        if secondary_score == primary_score and secondary_score > 0:
            # Ưu tiên archetype xuất hiện trong Q1 (câu hỏi quan trọng nhất)
            if 'Q1' in answers:
                q1_choice = answers['Q1']
                q1_data = self.discovery_questions['Q1']['choices'].get(q1_choice, {})
                q1_group = q1_data.get('group')
                if q1_group == secondary_group:
                    primary_group, secondary_group = secondary_group, primary_group
                    primary_score, secondary_score = secondary_score, primary_score
        
        # Kiểm tra điều kiện Synthesizer: ≥3 indicators
        is_synthesizer = (synthesizer_score >= 3)
        
        # Tính tỷ lệ xác suất archetype (P_archetype_i = WHY_i / ΣWHY)
        total_why_score = sum(archetype_scores.values())
        archetype_probability = primary_score / total_why_score if total_why_score > 0 else 0
        
        # Analyze style traits từ HOW
        style_counts = {}
        for style in style_traits:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        dominant_style = max(style_counts, key=style_counts.get) if style_counts else None
        
        # Tạo profile name
        profile_name = primary_group
        if is_synthesizer:
            profile_name += "–Synthesizer"
        
        return {
            'primary_group': primary_group,
            'secondary_group': secondary_group,
            'primary_score': primary_score,
            'secondary_score': secondary_score,
            'archetype_probability': round(archetype_probability, 2),
            'synthesizer_score': synthesizer_score,
            'is_synthesizer': is_synthesizer,
            'style_traits': style_traits,
            'style_counts': style_counts,
            'dominant_style': dominant_style,
            'profile_name': profile_name,
            'english_name': self.groups[primary_group] + ("–Synthesizer" if is_synthesizer else ""),
            'all_scores': archetype_scores,
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
    """Chạy ví dụ test theo tài liệu guide_11_11.md với 10 câu hỏi mới"""
    system = CaelioPersonalitySystem()
    
    # Ví dụ tạo profile Thinker-Synthesizer theo guide mới
    example_answers = {
        # WHY Section (Q1-Q4)
        'Q1': 'C',  # Tri thức: Mở ra bí mật
        'Q2': 'C',  # Tri thức: Giải mã bí ẩn
        'Q3': 'C',  # Tri thức: Giải mã thế giới
        'Q4': 'C',  # Tri thức: Cánh cửa tri thức
        
        # HOW Section (Q5-Q10)
        'Q5': 'C',  # Synthesizer +1: Nhà tổng hợp
        'Q6': 'A',  # High Power Distance: Tin chuyên gia
        'Q7': 'B',  # Introversion: Yên tĩnh nội tâm
        'Q8': 'B',  # Low Agreeableness: Nhân vật phức tạp
        'Q9': 'B',  # Low Neuroticism: Kịch tính gay cấn
        'Q10': 'C'  # Synthesizer +1: Kết nối đa ngành
    }
    
    profile = system.calculate_discovery_profile(example_answers)
    
    print("=== VÍ DỤ KIỂM TRA (Guide 11/11 - 10 câu mới) ===")
    print("Câu trả lời:", example_answers)
    print(f"\nProfile: {profile['profile_name']}")
    print(f"English: {profile['english_name']}")
    print(f"Primary Archetype: {profile['primary_group']} ({profile['primary_score']}/4 điểm WHY)")
    if profile['secondary_group']:
        print(f"Secondary Archetype: {profile['secondary_group']} ({profile['secondary_score']} điểm)")
    print(f"Archetype Probability: {profile['archetype_probability']*100:.0f}%")
    print(f"\nSynthesizer Score: {profile['synthesizer_score']}/6 possible")
    print(f"Is Synthesizer: {profile['is_synthesizer']} (cần ≥3)")
    print(f"\nStyle Traits: {profile['style_traits']}")
    print(f"Dominant Style: {profile['dominant_style']}")
    print(f"Style Counts: {profile['style_counts']}")
    
    print("\n📊 Kết quả mong đợi: Tri thức–Synthesizer")
    is_correct = (profile['is_synthesizer'] and 
                  profile['primary_group'] == 'Tri thức' and 
                  profile['synthesizer_score'] >= 2)
    print("✓ PASS" if is_correct else "✗ FAIL")

if __name__ == "__main__":
    # Chạy ví dụ kiểm tra trước
    run_example_test()
    
    print("\n" + "="*50)
    
    # Chạy test tương tác
    run_discovery_test()