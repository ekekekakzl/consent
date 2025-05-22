import streamlit as st
import openai
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    
    # API 키 입력
    api_key = st.text_input("OpenAI API Key", type="password", 
                           help="OpenAI API 키를 입력하세요")
    
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

# 초기 세션 상태 설정
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'understanding_score' not in st.session_state:
    st.session_state.understanding_score = {}
if 'consent_progress' not in st.session_state:
    st.session_state.consent_progress = 0

# LLM 설정 함수
def setup_llm(api_key):
    if api_key:
        openai.api_key = api_key
        return True
    return False

# 맞춤형 설명 생성 함수
def generate_explanation(content, user_profile, question_type="general"):
    if not setup_llm(api_key):
        return "API 키를 입력해주세요."
    
    # 사용자 프로필에 따른 프롬프트 생성
    profile_context = f"""
    사용자 프로필:
    - 연령대: {user_profile['age_group']}
    - 교육 수준: {user_profile['education_level']}
    - 의료 지식: {user_profile['medical_knowledge']}
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
    6. 필요시 시각적 설명 제안
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"설명 생성 중 오류가 발생했습니다: {str(e)}"

# 이해도 평가 함수
def evaluate_understanding(question, answer):
    evaluation_prompt = f"""
    다음 질문과 답변을 바탕으로 환자의 이해도를 1-10점으로 평가해주세요.
    
    질문: {question}
    답변: {answer}
    
    평가 기준:
    - 의료 용어 이해도
    - 수술 절차 이해도
    - 위험성 인지도
    - 전반적 이해도
    
    JSON 형태로 응답해주세요:
    {{"score": 점수, "feedback": "피드백", "areas_to_improve": ["개선영역1", "개선영역2"]}}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"score": 5, "feedback": "평가 중 오류가 발생했습니다.", "areas_to_improve": []}

# 메인 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["📋 동의서 설명", "❓ 질의응답", "📊 이해도 평가", "📈 진행 현황"])

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
            'education_level': education_level,
            'medical_knowledge': medical_knowledge,
            'language': language
        }
        
        explanation_request = f"{surgery_type}의 {selected_section}에 대해 자세히 설명해주세요."
        explanation = generate_explanation(explanation_request, user_profile)
        
        st.markdown(f'<div class="info-box">{explanation}</div>', unsafe_allow_html=True)
        
        # 추가 질문 제안
        if api_key:
            st.subheader("🤔 추가로 궁금한 점이 있으신가요?")
            suggested_questions = [
                f"{surgery_type} 수술 시간은 얼마나 걸리나요?",
                "로봇수술과 일반수술의 차이점은 무엇인가요?",
                "수술 후 회복 기간은 어느 정도인가요?",
                "수술 비용은 어느 정도 예상해야 하나요?"
            ]
            
            for question in suggested_questions:
                if st.button(question, key=f"suggest_{question}"):
                    answer = generate_explanation(question, user_profile)
                    st.markdown(f'<div class="success-box">{answer}</div>', unsafe_allow_html=True)

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
    
    # 이해도 점수 시각화
    if st.session_state.understanding_score:
        st.subheader("📊 이해도 변화 추이")
        
        df = pd.DataFrame(list(st.session_state.understanding_score.items()), 
                         columns=['항목', '점수'])
        
        fig = px.bar(df, x='항목', y='점수', 
                    title="항목별 이해도 점수",
                    color='점수',
                    color_continuous_scale='viridis')
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header"><h3>동의서 이해 진행 현황</h3></div>', 
                unsafe_allow_html=True)
    
    # 진행률 계산
    total_sections = len(consent_sections)
    completed_sections = st.session_state.consent_progress
    progress_percentage = (completed_sections / total_sections) * 100
    
    # 진행률 표시
    st.metric("전체 진행률", f"{progress_percentage:.1f}%", 
              f"{completed_sections}/{total_sections} 완료")
    
    progress_bar = st.progress(progress_percentage / 100)
    
    # 섹션별 체크리스트
    st.subheader("📝 동의서 항목별 체크리스트")
    
    col1, col2 = st.columns(2)
    
    for i, section in enumerate(consent_sections):
        with col1 if i % 2 == 0 else col2:
            if st.checkbox(section, key=f"section_{i}"):
                if i not in st.session_state.get('completed_items', set()):
                    st.session_state.consent_progress += 1
                    if 'completed_items' not in st.session_state:
                        st.session_state.completed_items = set()
                    st.session_state.completed_items.add(i)
    
    # 완료 상태 요약
    if progress_percentage == 100:
        st.success("🎉 모든 항목을 완료했습니다! 수술동의서에 대한 이해가 충분합니다.")
        
        if st.button("최종 이해도 리포트 생성"):
            st.markdown("""
            <div class="success-box">
                <h4>🏆 최종 이해도 리포트</h4>
                <p>• 전체 동의서 항목 완료: ✅</p>
                <p>• 질의응답 참여: ✅</p>
                <p>• 맞춤형 설명 이용: ✅</p>
                <p><strong>환자분께서 수술동의서 내용을 충분히 이해하셨습니다.</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    elif progress_percentage >= 50:
        st.warning(f"절반 이상 진행했습니다. 나머지 {total_sections - completed_sections}개 항목을 확인해주세요.")
    else:
        st.info("동의서 이해를 위해 각 항목을 차근차근 확인해주세요.")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏥 이 도구는 의료진의 진료를 대체하지 않습니다. 추가 궁금한 사항은 담당 의료진에게 문의하세요.</p>
    <p>📞 응급상황 시: 119 | 병원 대표번호: 1234-5678</p>
</div>
""", unsafe_allow_html=True)
