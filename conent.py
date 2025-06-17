import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로딩 방식 변경
# load_dotenv()

# OpenAI 클라이언트 설정

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit secrets를 확인하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# 페이지 설정
st.set_page_config(
    page_title="로봇수술동의서 이해증진도구",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1 style="color: white; text-align: center; margin: 0;">
        🤖 로봇수술동의서 이해증진도구
    </h1>
    <p style="color: white; text-align: center; margin: 0;">
        AI가 도와주는 수술동의서 맞춤형 설명 서비스
    </p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("🔧 설정")
    
    # 수술 유형 선택
    surgery_type = st.selectbox(
        "수술 유형 선택",
        ["다빈치 로봇 전립선절제술", "다빈치 로봇 담낭절제술", 
         "다빈치 로봇 위절제술", "다빈치 로봇 자궁절제술",
         "다빈치 로봇 심장수술", "기타"]
    )
    
    # 환자 특성
    st.subheader("환자 정보")
    age_group = st.selectbox("연령대", ["20-30대", "40-50대", "60-70대", "80대 이상"])
    education_level = st.selectbox("교육 수준", ["초등학교", "중학교", "고등학교", "대학교", "대학원"])
    medical_knowledge = st.selectbox("의료 지식 수준", ["전혀 없음", "기초", "보통", "높음"])
    
    # 언어 설정
    language = st.selectbox("설명 언어", ["한국어", "English", "中文", "日本語"])

    user_profile = {
    'age_group': age_group,
    'education_level': education_level,
    'medical_knowledge': medical_knowledge,
    'surgery_type': surgery_type,
    'language': language
}

    # 사용자 프로필에 따른 프롬프트 생성
    profile_context = f"""
    사용자 프로필:
    - 연령대: {user_profile['age_group']}
    - 교육 수준: {user_profile['education_level']}
    - 의료 지식: {user_profile['medical_knowledge']}
    - 수술 종류: {user_profile['surgery_type']}
    - 언어: {user_profile['language']}
    """
    
    system_prompt = f"""
    당신은 의료진과 환자 사이의 소통을 돕는 전문 의료 커뮤니케이션 AI입니다.
    
    {profile_context}
    
    다음 지침을 따라주세요:
    1. 사용자의 교육 수준과 의료 지식에 맞는 용어 사용
    2. 복잡한 의료 용어는 쉬운 말로 설명
    3. 구체적인 예시와 비유 활용
    4. 환자의 불안감을 줄이는 따뜻한 톤
    5. 정확하고 신뢰할 수 있는 정보 제공
    6. 반드시 300자 이내로 답변할 것
    7. 핵심적인 내용만 간단명료하게 설명
    """


def generate_explanation(prompt, profile):
    full_prompt = f"""
    사용자 프로필:
    - 연령대: {profile['age_group']}
    - 교육 수준: {profile['education_level']}
    - 의료 지식: {profile['medical_knowledge']}
    - 수술 종류: {profile['surgery_type']}
    - 언어: {profile['language']}

    설명 요청: {prompt}

    위 사용자에게 친절하고 이해하기 쉽게 300자 이내로 설명해 주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 의료 커뮤니케이션 전문가입니다."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {e}"


# 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["📋 동의서 설명", "❓ 질의응답", "📊 퀴즈"])

with tab1:
    st.markdown('<div class="section-header"><h3>수술동의서 맞춤형 설명</h3></div>', 
                unsafe_allow_html=True)
    
    # 동의서 섹션별 설명
    consent_sections = [
        "수술의 필요성과 목적",
        "수술 방법 및 절차",
        "로봇수술의 장단점", 
        "예상되는 합병증 및 위험성",
        "대안적 치료방법",
        "수술 후 주의사항",
        "비용 및 보험적용"
    ]
    
    selected_section = st.selectbox("설명을 듣고 싶은 항목을 선택하세요:", consent_sections)
    
    if st.button("맞춤형 설명 생성", type="primary"):
        user_profile = {
            'age_group': age_group,
            'surgery_type': surgery_type,
            'education_level': education_level,
            'medical_knowledge': medical_knowledge,
            'language': language
        }
        explanation_request = f"{surgery_type}의 {selected_section}에 대해 자세히 설명해주세요."
        explanation = generate_explanation(explanation_request, user_profile)

        st.markdown(f'<div class="info-box">{explanation}</div>', unsafe_allow_html=True)


        # 추가 질문 섹션을 챗봇 형식으로 변경
        if os.getenv("OPENAI_API_KEY"):
            st.markdown("""
            <div style='margin: 2rem 0;'>
                <div class="section-header">
                    <h4>🤖 추가로 궁금하신 점이 있으신가요?</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 채팅 히스토리 표시
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.additional_chat_history:
                    if chat["role"] == "user":
                        st.markdown(f"""
                        <div style='display: flex; justify-content: flex-end; margin: 1rem 0;'>
                            <div style='background-color: #e9ecef; padding: 0.8rem; border-radius: 15px; max-width: 80%;'>
                                <p style='margin: 0;'>{chat["content"]}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='display: flex; margin: 1rem 0;'>
                            <div style='background-color: #007bff; color: white; padding: 0.8rem; border-radius: 15px; max-width: 80%;'>
                                <p style='margin: 0;'>{chat["content"]}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # 직접 질문 입력
            st.markdown("<div style='margin-top: 2rem;'><h5>✍️ 직접 질문하기</h5></div>", unsafe_allow_html=True)
            user_question = st.text_input("질문을 입력해주세요:", key="additional_question")
            
            # 전송 버튼
            if st.button("전송", key="send_additional"):
                if user_question:
                    user_profile = {
                        'age_group': age_group,
                        'education_level': education_level,
                        'medical_knowledge': medical_knowledge,
                        'language': language
                    }
                    
                    # 사용자 질문을 히스토리에 추가
                    st.session_state.additional_chat_history.append({
                        "role": "user",
                        "content": user_question
                    })
                    
                    # AI 응답 생성
                    answer = generate_explanation(user_question, user_profile)
                    
                    # AI 응답을 히스토리에 추가
                    st.session_state.additional_chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                    st.rerun()

            # 추천 질문 버튼들
            st.markdown("<div style='margin-top: 2rem;'><h5>💡 자주 묻는 질문</h5></div>", unsafe_allow_html=True)
            
            # 더 많은 추천 질문 추가
            suggested_questions = [
                f"{surgery_type} 수술 시간은 얼마나 걸리나요?",
                "로봇수술과 일반수술의 차이점은 무엇인가요?",
                "수술 후 회복 기간은 어느 정도인가요?",
                "수술 비용은 어느 정도 예상해야 하나요?",
                "수술 후 통증은 어느 정도인가요?",
                "수술 후 일상생활 복귀는 언제 가능한가요?",
                "수술 전 주의사항은 무엇인가요?",
                "수술 후 관리는 어떻게 해야 하나요?"
            ]
            
            # 2열로 버튼 배치
            cols = st.columns(2)
            for i, question in enumerate(suggested_questions):
                with cols[i % 2]:
                    if st.button(f"🔍 {question}", key=f"suggest_{i}", 
                               use_container_width=True,
                               help="클릭하시면 답변이 생성됩니다"):
                        user_profile = {
                            'age_group': age_group,
                            'education_level': education_level,
                            'medical_knowledge': medical_knowledge,
                            'language': language
                        }
                        
                        # 사용자 질문을 히스토리에 추가
                        st.session_state.additional_chat_history.append({
                            "role": "user",
                            "content": question
                        })
                        
                        # AI 응답 생성
                        answer = generate_explanation(question, user_profile)
                        
                        # AI 응답을 히스토리에 추가
                        st.session_state.additional_chat_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        st.rerun()

with tab2:
    st.markdown('<div class="section-header"><h3>실시간 질의응답</h3></div>', 
                unsafe_allow_html=True)
    
    # 채팅 인터페이스
    user_question = st.text_area("궁금한 점을 자유롭게 질문해주세요:", 
                                placeholder="예: 로봇수술 후 통증은 어느 정도인가요?")
    
    if st.button("질문하기", type="primary"):
        if user_question and api_key:
            user_profile = {
                'age_group': age_group,
                'education_level': education_level,
                'medical_knowledge': medical_knowledge,
                'language': language
            }
            
            answer = generate_explanation(user_question, user_profile, "qa")
            
            # 채팅 히스토리에 추가
            st.session_state.chat_history.append({
                "timestamp": datetime.now().strftime("%H:%M"),
                "question": user_question,
                "answer": answer
            })
    
    # 채팅 히스토리 표시
    if st.session_state.chat_history:
        st.subheader("💬 대화 내역")
        for chat in reversed(st.session_state.chat_history[-5:]):  # 최근 5개만 표시
            with st.expander(f"[{chat['timestamp']}] {chat['question'][:50]}..."):
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer']}")

with tab3:
    st.markdown('<div class="section-header"><h3>이해도 평가 및 맞춤 학습</h3></div>', 
                unsafe_allow_html=True)
    
    # 퀴즈 생성
    quiz_topics = [
        "수술 방법 이해도",
        "위험성 인지도", 
        "수술 후 관리",
        "로봇수술 특성"
    ]
    
    selected_quiz = st.selectbox("평가 주제 선택:", quiz_topics)
    
    if st.button("평가 문제 생성"):
        if api_key:
            quiz_prompt = f"""
            {surgery_type}에 대한 {selected_quiz} 관련 객관식 문제를 생성해주세요.
            환자의 수준: {education_level}, 의료지식: {medical_knowledge}
            
            다음 형식으로 답해주세요:
            문제: [문제 내용]
            1) 선택지1
            2) 선택지2  
            3) 선택지3
            4) 선택지4
            정답: [번호]
            해설: [설명]
            """
            
            quiz_content = generate_explanation(quiz_prompt, {
                'age_group': age_group,
                'education_level': education_level,
                'medical_knowledge': medical_knowledge,
                'language': language
            })
            
            st.markdown(f'<div class="info-box">{quiz_content}</div>', unsafe_allow_html=True)

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏥 이 도구는 의료진의 진료를 대체하지 않습니다. 추가 궁금한 사항은 담당 의료진에게 문의하세요.</p>
    <p>📞 응급상황 시: 119 | 병원 대표번호: 1234-5678</p>
</div>
""", unsafe_allow_html=True)
