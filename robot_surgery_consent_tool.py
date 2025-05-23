import streamlit as st
import sys
import subprocess
import os
from pathlib import Path

# 필요한 패키지 설치
try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# OpenAI 모듈이 없을 경우 자동으로 설치
try:
    from openai import OpenAI
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==0.28.0"])
    from openai import OpenAI

import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 환경 변수 로드
def load_api_key():
    # .env 파일 로드
    env_path = Path('.') / '.env'
    load_dotenv(env_path)
    
    # 환경 변수에서 API 키 가져오기
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # API 키가 환경 변수에 없으면 세션 상태에서 확인
        if 'openai_api_key' in st.session_state:
            api_key = st.session_state.openai_api_key
    
    return api_key

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
    
    # API 키 입력 (환경 변수에서 가져오기)
    api_key = load_api_key()
    if not api_key:
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="OpenAI API 키를 입력하세요. 입력한 키는 환경 변수에 저장됩니다."
        )
        if api_key:
            st.session_state.openai_api_key = api_key
            # API 키를 .env 파일에 저장
            with open('.env', 'w') as f:
                f.write(f'OPENAI_API_KEY={api_key}')
            st.success("API 키가 저장되었습니다!")
    
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
if 'additional_chat_history' not in st.session_state:
    st.session_state.additional_chat_history = []

# LLM 설정 함수
def setup_llm():
    api_key = load_api_key()
    if api_key:
        return OpenAI(api_key=api_key)
    return None

# 맞춤형 설명 생성 함수
def generate_explanation(content, user_profile, question_type="general"):
    client = setup_llm()
    if not client:
        return "OpenAI API 키를 입력해주세요."
    
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
    6. 반드시 100자 이내로 답변할 것
    7. 핵심적인 내용만 간단명료하게 설명
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 질문에 대해 100자 이내로 답변해주세요: {content}"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        answer = response.choices[0].message.content
        # 100자로 제한
        if len(answer) > 100:
            answer = answer[:97] + "..."
        return answer
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg:
            return "⚠️ API 사용량이 초과되었습니다."
        elif "invalid_request_error" in error_msg:
            return "⚠️ 잘못된 API 요청입니다."
        elif "invalid_api_key" in error_msg:
            return "⚠️ 유효하지 않은 API 키입니다."
        else:
            return "⚠️ 오류가 발생했습니다."

# 이해도 평가 함수
def evaluate_understanding(question, answer):
    client = setup_llm()
    if not client:
        return {"score": 5, "feedback": "OpenAI API 키가 설정되지 않았습니다.", "areas_to_improve": []}

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg:
            return {
                "score": 0,
                "feedback": "API 사용량이 초과되었습니다. 관리자에게 문의해주세요.",
                "areas_to_improve": ["API 키 확인 필요"]
            }
        else:
            return {
                "score": 0,
                "feedback": f"평가 중 오류가 발생했습니다: {error_msg}",
                "areas_to_improve": []
            }

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
        
        # 추가 질문 섹션을 챗봇 형식으로 변경
        if api_key:
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
