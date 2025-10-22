"""
Web Interface cho hệ thống Caelio Personality Test
Chạy bằng Streamlit
"""

import streamlit as st
import pandas as pd
from caelio_personality_system import CaelioPersonalitySystem
from caelio_book_matcher import CaelioBookMatcher

# Cấu hình trang
st.set_page_config(
    page_title="Caelio Personality Test",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("📚 Caelio - Hệ thống gợi ý sách theo tính cách")
    st.markdown("*Khám phá cuốn sách phù hợp với tính cách đọc của bạn*")
    
    # Khởi tạo session state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'journey_type' not in st.session_state:
        st.session_state.journey_type = None
    if 'profile_result' not in st.session_state:
        st.session_state.profile_result = None
    
    # Khởi tạo hệ thống
    personality_system = CaelioPersonalitySystem()
    book_matcher = CaelioBookMatcher()
    
    # Bước 1: Chọn hành trình
    if st.session_state.journey_type is None:
        show_journey_selection()
    
    # Bước 2: Trả lời câu hỏi
    elif st.session_state.profile_result is None:
        if st.session_state.journey_type == 'discovery':
            show_discovery_questions(personality_system)
        else:
            st.warning("Hành trình chuyên ngành đang được phát triển...")
            if st.button("Quay lại chọn hành trình"):
                reset_test()
    
    # Bước 3: Hiển thị kết quả
    else:
        show_results(book_matcher)

def show_journey_selection():
    """Hiển thị màn hình chọn hành trình"""
    st.header("🎯 Khi đến với Caelio, bạn đang tìm kiếm điều gì?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 Hành trình Khám phá
        **"Một cuốn sách khiến tôi nhìn thấy chính mình theo một cách mới"**
        
        Dành cho những ai muốn:
        - Khám phá bản thân qua sách
        - Tìm hiểu phong cách đọc của mình
        - Được gợi ý sách phù hợp với tính cách
        """)
        
        if st.button("🚀 Bắt đầu hành trình Khám phá", use_container_width=True):
            st.session_state.journey_type = 'discovery'
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🎓 Hành trình Chuyên ngành
        **"Một cuốn sách giúp tôi học, làm việc hoặc nghiên cứu hiệu quả hơn"**
        
        Dành cho những ai muốn:
        - Đọc sách chuyên ngành
        - Nâng cao kiến thức lĩnh vực
        - Phát triển nghề nghiệp
        """)
        
        if st.button("🎯 Bắt đầu hành trình Chuyên ngành", use_container_width=True):
            st.session_state.journey_type = 'professional'
            st.rerun()

def show_discovery_questions(personality_system):
    """Hiển thị câu hỏi hành trình khám phá"""
    questions = list(personality_system.discovery_questions.items())
    current_q = st.session_state.current_question
    
    if current_q >= len(questions):
        # Tính toán kết quả
        profile = personality_system.calculate_discovery_profile(st.session_state.answers)
        st.session_state.profile_result = profile
        st.rerun()
        return
    
    q_id, question_data = questions[current_q]
    
    # Progress bar
    progress = (current_q + 1) / len(questions)
    st.progress(progress)
    st.text(f"Câu {current_q + 1}/{len(questions)}")
    
    # Hiển thị câu hỏi
    st.header(f"📋 {question_data['question']}")
    
    # Hiển thị lựa chọn
    choices = question_data['choices']
    choice_texts = [f"{key}. {data['text']}" for key, data in choices.items()]
    
    selected = st.radio(
        "Chọn câu trả lời phù hợp nhất:",
        options=list(choices.keys()),
        format_func=lambda x: f"{x}. {choices[x]['text']}",
        key=f"q_{q_id}"
    )
    
    # Nút điều hướng
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q > 0:
            if st.button("⬅️ Câu trước"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col3:
        if selected:
            if st.button("➡️ Câu tiếp theo"):
                st.session_state.answers[q_id] = selected
                st.session_state.current_question += 1
                st.rerun()

def show_results(book_matcher):
    """Hiển thị kết quả phân tích"""
    profile = st.session_state.profile_result
    
    st.header("🎉 Kết quả phân tích tính cách đọc sách của bạn")
    
    # Hiển thị profile chính
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ## 🏷️ {profile['profile_name']}
        **Tên tiếng Anh:** {profile['english_name']}
        
        ### 📊 Chi tiết điểm số:
        - **Nhóm chính:** {profile['primary_group']} ({profile['primary_score']} điểm)
        - **Nhóm phụ:** {profile['secondary_group']} ({profile['secondary_score']} điểm)
        - **Điểm Synthesizer:** {profile['synthesizer_score']}/8
        - **Là Synthesizer:** {"✅ Có" if profile['is_synthesizer'] else "❌ Không"}
        - **Đa động lực:** {"✅ Có" if profile['is_multi_motivated'] else "❌ Không"}
        """)
    
    with col2:
        # Biểu đồ điểm số
        scores_df = pd.DataFrame(
            list(profile['all_scores'].items()),
            columns=['Nhóm', 'Điểm']
        )
        st.bar_chart(scores_df.set_index('Nhóm'))
    
    # Mô tả nhóm tính cách
    show_personality_description(profile)
    
    # Gợi ý sách
    show_book_recommendations(profile, book_matcher)
    
    # Nút reset
    if st.button("🔄 Làm lại bài test", use_container_width=True):
        reset_test()

def show_personality_description(profile):
    """Hiển thị mô tả chi tiết về nhóm tính cách"""
    descriptions = {
        'Kết nối': {
            'title': '🤝 The Connectors - Người Kết nối',
            'description': 'Bạn đọc sách để tìm kiếm sự hòa hợp, tình yêu và cảm giác thuộc về. Bạn thích những câu chuyện chạm đến trái tim, giúp bạn hiểu và đồng cảm với người khác.',
            'books': 'Tâm lý tình cảm, chữa lành, tản văn, tiểu thuyết gia đình'
        },
        'Tự do': {
            'title': '🕊️ The Individuals - Người Tự do',
            'description': 'Bạn tìm kiếm tự do, thể hiện bản sắc cá nhân và phá vỡ khuôn mẫu. Đọc sách là cách bạn khám phá thế giới và định hình cá tính riêng.',
            'books': 'Du ký, nghệ thuật sống, tiểu thuyết sáng tạo, sách phản tư xã hội'
        },
        'Tri thức': {
            'title': '🧠 The Thinkers - Người Tư duy',
            'description': 'Bạn tìm kiếm tri thức, sự thật và lý giải thế giới. Mỗi cuốn sách là một câu hỏi cần được trả lời, một bí ẩn cần được khám phá.',
            'books': 'Khoa học phổ thông, triết học, lịch sử, sách phân tích chuyên sâu'
        },
        'Chinh phục': {
            'title': '🏆 The Achievers - Người Chinh phục',
            'description': 'Bạn muốn vượt qua thử thách, tạo ra thành tựu và biến ý tưởng thành hiện thực. Sách là công cụ giúp bạn đạt được mục tiêu.',
            'books': 'Sách truyền cảm hứng, lãnh đạo, chiến lược, hồi ký thành công'
        },
        'Kiến tạo': {
            'title': '🏗️ The Builders - Người Xây dựng',
            'description': 'Bạn muốn xây dựng nền tảng vững chắc, phát triển kỹ năng thực tế. Bạn thích những cuốn sách có tính ứng dụng cao.',
            'books': 'Sách kỹ năng, tài chính, marketing, khởi nghiệp, sách hướng nghiệp'
        }
    }
    
    primary_group = profile['primary_group']
    desc = descriptions[primary_group]
    
    st.markdown(f"""
    ### {desc['title']}
    {desc['description']}
    
    **Thể loại sách phù hợp:** {desc['books']}
    """)
    
    if profile['is_synthesizer']:
        st.info("""
        🔗 **Đặc điểm Synthesizer của bạn:**
        Bạn có khả năng tư duy tổng hợp cao, thích kết nối tri thức từ nhiều lĩnh vực khác nhau. 
        Bạn phù hợp với những cuốn sách có chiều sâu, khả năng liên kết đa ngành và gợi mở tư duy phản tư.
        """)

def show_book_recommendations(profile, book_matcher):
    """Hiển thị gợi ý sách"""
    st.header("📖 Gợi ý sách dành cho bạn")
    
    try:
        # Load dữ liệu sách
        book_df = pd.read_csv('dataset/books_full_data.csv')
        
        # Lấy gợi ý
        result = book_matcher.get_personalized_recommendations(
            st.session_state.answers, 
            book_df, 
            top_n=10
        )
        
        if len(result['recommendations']) > 0:
            st.success(f"Tìm thấy {result['total_matches']} cuốn sách phù hợp với tính cách của bạn!")
            
            # Hiển thị top sách
            for i, (_, book) in enumerate(result['recommendations'].head(5).iterrows()):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **{i+1}. {book['title']}**
                        - Tác giả: {book.get('authors', 'N/A')}
                        - Thể loại: {book['category']}
                        - Độ phù hợp: {book['personality_match_score']:.0%}
                        """)
                    
                    with col2:
                        if 'cover_link' in book and pd.notna(book['cover_link']):
                            try:
                                st.image(book['cover_link'], width=80)
                            except:
                                st.text("📚")
                        else:
                            st.text("📚")
            
            # Thống kê thể loại
            st.subheader("📊 Phân bố thể loại phù hợp")
            category_dist = pd.Series(result['match_distribution'])
            st.bar_chart(category_dist)
        
        else:
            st.warning("Không tìm thấy sách phù hợp trong cơ sở dữ liệu.")
    
    except FileNotFoundError:
        st.error("Không tìm thấy file dữ liệu sách. Vui lòng kiểm tra file 'dataset/books_full_data.csv'")
        
        # Hiển thị gợi ý chung
        recommendations = book_matcher.personality_system.get_book_recommendations(profile)
        st.markdown("**Thể loại sách được gợi ý cho bạn:**")
        for rec in recommendations:
            st.markdown(f"- {rec}")

def reset_test():
    """Reset toàn bộ test"""
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.journey_type = None
    st.session_state.profile_result = None
    st.rerun()

if __name__ == "__main__":
    main()