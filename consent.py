import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# 환경 변수 로딩 방식 변경
# load_dotenv()

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'additional_chat_history' not in st.session_state:
    st.session_state.additional_chat_history = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'pre_quiz_completed' not in st.session_state:
    st.session_state.pre_quiz_completed = False
if 'post_quiz_completed' not in st.session_state:
    st.session_state.post_quiz_completed = False
if 'post_quiz_answers' not in st.session_state:
    st.session_state.post_quiz_answers = {}
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'section_scores' not in st.session_state:
    st.session_state.section_scores = {}
if 'profile_setup_completed' not in st.session_state:
    st.session_state.profile_setup_completed = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
if 'all_users_data' not in st.session_state:
    st.session_state.all_users_data = []
if 'post_quiz_score' not in st.session_state:
    st.session_state.post_quiz_score = 0
if 'user_data' not in st.session_state:
    st.session_state.user_data = []

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

# 기본 제목 숨기기
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > header {
        background-color: transparent;
    }
    .stApp {
        margin-top: -100px;
    }
</style>
""", unsafe_allow_html=True)

# CSS 스타일링 - 큰 글씨 적용
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        font-size: 3rem !important;
        font-weight: bold !important;
        color: white !important;
        margin-bottom: 1rem;
    }
    .main-header p {
        font-size: 1.5rem !important;
        color: white !important;
    }
    .section-header {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        text-align: center;
    }
    .section-header h3, .section-header h4 {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        margin: 0;
    }
    .info-box {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .info-box h4 {
        font-size: 1.6rem !important;
        font-weight: bold !important;
        margin-bottom: 1rem;
    }
    .warning-box {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .warning-box h4 {
        font-size: 1.6rem !important;
        font-weight: bold !important;
        margin-bottom: 1rem;
    }
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .success-box h4 {
        font-size: 1.6rem !important;
        font-weight: bold !important;
        margin-bottom: 1rem;
    }
    .quiz-box {
        background: #f5f5f5;
        border-left: 3px solid #4CAF50;
        padding: 0.8rem;
        margin: 0.8rem 0;
        border-radius: 4px;
    }
    .quiz-question {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.4rem;
    }
    .quiz-option {
        margin: 0.8rem 0;
        padding: 0.8rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1.2rem !important;
    }
    .quiz-option:hover {
        background-color: #e9ecef;
    }
    .profile-box {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 2rem 0;
        font-size: 1.2rem !important;
    }
    .profile-box h3 {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        margin-bottom: 1.5rem;
        color: #667eea;
    }
    
    /* 일반 텍스트 크기 증가 */
    .stMarkdown, .stText, .stSelectbox, .stRadio, .stButton {
        font-size: 1.2rem !important;
    }
    
    /* 탭 텍스트 크기 */
    .stTabs [data-baseweb="tab-list"] {
        font-size: 1.4rem !important;
    }
    
    /* 버튼 텍스트 크기 */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.4rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }
    
    .stButton > button:disabled {
        background: #ccc;
        transform: none;
        box-shadow: none;
    }
    
    /* 라디오 버튼 텍스트 크기 */
    .stRadio > div > div > div > label {
        font-size: 1.2rem !important;
    }
    
    /* 셀렉트박스 텍스트 크기 */
    .stSelectbox > div > div > div > div {
        font-size: 1.2rem !important;
    }
    
    /* 헤더 텍스트 크기 */
    h1, h2, h3, h4, h5, h6 {
        font-size: 1.5rem !important;
    }
    
    /* 일반 텍스트 크기 */
    p, div, span {
        font-size: 1.2rem !important;
    }
    
    /* 진행률 바 크기 */
    .stProgress > div > div > div {
        height: 20px !important;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        margin-left: auto;
    }
    
    .assistant-message {
        background: #f1f3f4;
        color: #2c3e50;
        margin-right: auto;
    }
    
    .admin-toggle {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
    }
    
    .admin-dashboard {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border: 2px solid #4CAF50;
    }
    
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.4rem;
    }
    
    .stats-number {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4CAF50;
    }
    
    .stats-label {
        color: #666;
        margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🤖 로봇수술동의서 이해증진도구</h1>
    <p>로봇수술에 대한 이해를 도와드리겠습니다.</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 네비게이션
def render_sidebar_navigation():
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h3>🤖 네비게이션</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 프로필 설정이 완료된 경우에만 네비게이션 표시
    if st.session_state.get('profile_setup_completed', False):
        if st.sidebar.button("🏠 메인 페이지", key="nav_main"):
            st.session_state.current_page = "main"
            st.rerun()
        
        if st.sidebar.button("📝 사전 퀴즈", key="nav_pre_quiz"):
            st.session_state.current_page = "pre_quiz"
            st.rerun()
        
        if st.sidebar.button("📚 로봇수술 정보", key="nav_info"):
            st.session_state.current_page = "info"
            st.rerun()
        
        # 사전 퀴즈가 완료된 경우에만 사후 퀴즈 표시
        if st.session_state.get('pre_quiz_completed', False):
            if st.sidebar.button("📊 사후 퀴즈", key="nav_post_quiz"):
                st.session_state.current_page = "post_quiz"
                st.rerun()
        
        if st.sidebar.button("💬 질문하기", key="nav_chat"):
            st.session_state.current_page = "chat"
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # 현재 페이지 표시
        current_page_names = {
            "main": "메인 페이지",
            "pre_quiz": "사전 퀴즈",
            "info": "로봇수술 정보",
            "post_quiz": "사후 퀴즈",
            "chat": "질문하기",
            "admin": "관리자 대시보드"
        }
        
        current_page_name = current_page_names.get(st.session_state.current_page, "메인 페이지")
        st.sidebar.markdown(f"""
        <div style="background-color: #e7f3ff; padding: 0.5rem; border-radius: 5px; text-align: center;">
            <strong>현재: {current_page_name}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # 관리자 모드 (사이드바 맨 아래)
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 0.5rem; background-color: #f8f9fa; border-radius: 5px; margin-top: 2rem;">
        <small style="color: #666;">🔧 관리자</small>
    </div>
    """, unsafe_allow_html=True)
    
    admin_mode = st.sidebar.checkbox("관리자 모드", key="admin_toggle")
    if admin_mode:
        st.session_state.admin_mode = True
        if st.sidebar.button("📊 대시보드", key="nav_admin", use_container_width=True):
            st.session_state.current_page = "admin"
            st.rerun()
    else:
        st.session_state.admin_mode = False

# 사용자 프로필 설정
def render_profile_setup():
    st.markdown("""
    <div class="profile-box">
        <h3>👤 나에게 맞는 항목을 선택해주세요</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.selectbox(
            "나이",
            ["20-30대", "30-40대", "40-50대", "50-60대", "60-70대", "70대 이상"],
            key="age"
        )
        
        gender = st.selectbox(
            "성별",
            ["남성", "여성"],
            key="gender"
        )
    
    with col2:
        education = st.selectbox(
            "교육 수준",
            ["고등학교 졸업", "대학교 졸업", "대학원 졸업", "기타"],
            key="education"
        )
        
        medical_experience = st.selectbox(
            "수술 유형",
            ["비뇨기과", "산부인과", "흉부외과", "외과", "기타"],
            key="medical_experience"
        )
    
    if st.button("확인", key="profile_submit"):
        st.session_state.profile_setup_completed = True
        st.session_state.user_profile = {
            "age": age,
            "gender": gender,
            "education": education,
            "medical_experience": medical_experience
        }
        st.success("감사합니다. 먼저 몇가지 퀴즈를 풀어보세요!")
        st.rerun()

# 사전 퀴즈
def render_pre_quiz():
    st.markdown("""
    <div class="section-header">
        <h3>📝 사전 이해도 평가</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>안내</h4>
        <p>로봇수술에 대한 현재 이해도를 평가하기 위한 퀴즈입니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 세션 상태 확인
    current_section = st.session_state.get('current_section', 0)
    
    # Ⅰ. 수술 목적 및 과정 (4문항)
    if current_section == 0:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅰ. 수술 목적 및 과정 (4문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        questions_section1 = {
            "q1": {
                "question": "1. 로봇보조수술의 장점이 아닌 것은?",
                "options": [
                    "절개 부위가 작아 회복이 빠를 수 있다",
                    "로봇 팔을 통해 정밀한 조작이 가능하다",
                    "수술 중 로봇이 자율적으로 판단하여 수술을 진행한다",
                    "출혈 및 감염 위험이 줄어들 수 있다"
                ],
                "correct": 2
            },
            "q2": {
                "question": "2. 수술 부위에 2cm 정도의 절개를 몇 군데 낼까요?",
                "options": [
                    "1~2곳",
                    "2~3곳",
                    "3~5곳",
                    "5~7곳"
                ],
                "correct": 2
            },
            "q3": {
                "question": "3. 로봇보조수술 시 의사는 어떤 방식으로 수술을 수행하나요?",
                "options": [
                    "로봇이 자동으로 수행하며 의사는 모니터링만 한다",
                    "외과의가 직접 기구를 손으로 조작한다",
                    "외과의가 콘솔을 통해 로봇 팔을 원격으로 조작한다",
                    "인공지능이 수술 계획을 분석한 후 자율로 시행한다"
                ],
                "correct": 2
            },
            "q4": {
                "question": "4. 로봇수술 도중 개복수술로 바뀔 수 있는 상황이 아닌 것은?",
                "options": [
                    "장(창자)이 서로 붙어 있는 '유착'이 심할 때",
                    "피가 많이 날 때",
                    "혹이 암일지도 몰라서 더 자세히 확인해야 할 때",
                    "로봇 팔이 깊은 곳까지 들어갈 때"
                ],
                "correct": 3
            }
        }
        
        for q_id, q_data in questions_section1.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.quiz_answers[q_id] = q_data['options'].index(answer)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_section1", disabled=True):
                pass
        with col2:
            if st.button("다음", key="next_section1"):
                st.session_state.current_section = 1
                st.rerun()
    
    # Ⅱ. 수술 위험 및 합병증과 관리 (4문항)
    elif current_section == 1:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅱ. 수술 위험 및 합병증과 관리 (4문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        questions_section2 = {
            "q5": {
                "question": "5. 로봇 수술에서 임파선 적출 후 생길 수 있는 부작용은 무엇인가요?",
                "options": [
                    "혈압 상승",
                    "임파액 정체로 인한 부종",
                    "심장 두근거림",
                    "시야 흐림"
                ],
                "correct": 1
            },
            "q6": {
                "question": "6. 수술 후 폐에 문제가 생기는 것을 예방하기 위해 어떤 행동이 도움이 될까요?",
                "options": [
                    "움직이지 말고 계속 누워 있기",
                    "말을 적게 하고 조용히 있기",
                    "깊게 숨 쉬기 운동을 하고, 조금씩 자주 움직이기",
                    "얕고 빠르게 숨쉬기 운동하기"
                ],
                "correct": 2
            },
            "q7": {
                "question": "7. 무통주사(아픈 걸 줄여주는 주사)를 맞을 때 생길 수 있는 일은?",
                "options": [
                    "속이 울렁거리고 어지러울 수 있어요",
                    "갑자기 땀이 나요",
                    "배가 아프고 손이 떨려요",
                    "기침이 멈추지 않아요"
                ],
                "correct": 0
            },
            "q8": {
                "question": "8. 장(창자)이 서로 붙는 걸 '유착'이라고 해요. 유착을 막으려면 어떻게 해야 할까요?",
                "options": [
                    "가만히 누워 있기",
                    "수술 다음 날부터 걷기 운동하기",
                    "음식을 전혀 먹지 않기",
                    "배를 누르면서 운동하기"
                ],
                "correct": 1
            }
        }
        
        for q_id, q_data in questions_section2.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.quiz_answers[q_id] = q_data['options'].index(answer)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_section2"):
                st.session_state.current_section = 0
                st.rerun()
        with col2:
            if st.button("다음", key="next_section2"):
                st.session_state.current_section = 2
                st.rerun()
    
    # Ⅲ. 자기결정권 (2문항)
    elif current_section == 2:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅲ. 자기결정권 (2문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        questions_section3 = {
            "q9": {
                "question": "9. 수술에 대한 선택은 누가 최종적으로 결정하나요?",
                "options": [
                    "의사",
                    "가족",
                    "환자"
                ],
                "correct": 2
            },
            "q10": {
                "question": "10. 자기결정권에 해당하지 않는 내용은 무엇인가요?",
                "options": [
                    "설명을 듣고 동의한다",
                    "잘 모르니 의료진에게 맡긴다.",
                    "부작용 가능성을 인지한다.",
                    "언제든 수술동의를 철회할 수 있다."
                ],
                "correct": 0
            }
        }
        
        for q_id, q_data in questions_section3.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.quiz_answers[q_id] = q_data['options'].index(answer)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_section3"):
                st.session_state.current_section = 1
                st.rerun()
        with col2:
            if st.button("퀴즈 제출", key="pre_quiz_submit"):
                st.session_state.pre_quiz_completed = True
                st.session_state.current_section = 0  # 다음 사용자를 위해 초기화
                st.success("퀴즈가 제출되었습니다!")
                st.rerun()

# 사후 퀴즈
def render_post_quiz():
    st.markdown("""
    <div class="section-header">
        <h3>📝 사후 이해도 평가</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>안내</h4>
        <p>로봇수술 정보를 학습한 후 이해도를 평가하기 위한 퀴즈입니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 세션 상태 확인
    current_section = st.session_state.get('current_section', 0)
    
    # Ⅰ. 수술 목적 및 과정 (4문항)
    if current_section == 0:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅰ. 수술 목적 및 과정 (4문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        post_questions_section1 = {
            "pq1": {
                "question": "1. 로봇보조수술의 장점이 아닌 것은?",
                "options": [
                    "절개 부위가 작아 회복이 빠를 수 있다",
                    "로봇 팔을 통해 정밀한 조작이 가능하다",
                    "수술 중 로봇이 자율적으로 판단하여 수술을 진행한다",
                    "출혈 및 감염 위험이 줄어들 수 있다"
                ],
                "correct": 2,
                "explanation": "로봇수술은 의사가 콘솔을 통해 로봇 팔을 조작하는 방식입니다. 로봇이 자율적으로 판단하여 수술을 진행하는 것은 아닙니다."
            },
            "pq2": {
                "question": "2. 수술 부위에 2cm 정도의 절개를 몇 군데 낼까요?",
                "options": [
                    "1~2곳",
                    "2~3곳",
                    "3~5곳",
                    "5~7곳"
                ],
                "correct": 2,
                "explanation": "로봇수술에서는 보통 3~5곳에 작은 절개를 만들어 로봇 팔과 카메라를 삽입합니다."
            },
            "pq3": {
                "question": "3. 로봇보조수술 시 의사는 어떤 방식으로 수술을 수행하나요?",
                "options": [
                    "로봇이 자동으로 수행하며 의사는 모니터링만 한다",
                    "외과의가 직접 기구를 손으로 조작한다",
                    "외과의가 콘솔을 통해 로봇 팔을 원격으로 조작한다",
                    "인공지능이 수술 계획을 분석한 후 자율로 시행한다"
                ],
                "correct": 2,
                "explanation": "의사는 콘솔에 앉아서 3D 영상을 보면서 로봇 팔을 원격으로 조작하여 수술을 수행합니다."
            },
            "pq4": {
                "question": "4. 로봇수술 도중 개복수술로 바뀔 수 있는 상황이 아닌 것은?",
                "options": [
                    "장(창자)이 서로 붙어 있는 '유착'이 심할 때",
                    "피가 많이 날 때",
                    "혹이 암일지도 몰라서 더 자세히 확인해야 할 때",
                    "로봇 팔이 깊은 곳까지 들어갈 때"
                ],
                "correct": 3,
                "explanation": "로봇 팔이 깊은 곳까지 들어가는 것은 정상적인 수술 과정입니다. 유착, 출혈, 암 의심 등의 상황에서 개복수술로 전환될 수 있습니다."
            }
        }
        
        for q_id, q_data in post_questions_section1.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.post_quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.post_quiz_answers[q_id] = q_data['options'].index(answer)
                
                # 정답을 클릭했을 때만 해설 표시
                if st.session_state.post_quiz_answers[q_id] == q_data['correct']:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ 정답입니다!</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>❌ 틀렸습니다.</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_post_section1", disabled=True):
                pass
        with col2:
            if st.button("다음", key="next_post_section1"):
                st.session_state.current_section = 1
                st.rerun()
    
    # Ⅱ. 수술 위험 및 합병증과 관리 (4문항)
    elif current_section == 1:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅱ. 수술 위험 및 합병증과 관리 (4문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        post_questions_section2 = {
            "pq5": {
                "question": "5. 로봇 수술에서 임파선 적출 후 생길 수 있는 부작용은 무엇인가요?",
                "options": [
                    "혈압 상승",
                    "임파액 정체로 인한 부종",
                    "심장 두근거림",
                    "시야 흐림"
                ],
                "correct": 1,
                "explanation": "임파선을 제거하면 임파액의 흐름이 막혀서 부종이 생길 수 있습니다. 이는 정상적인 수술 후 현상입니다."
            },
            "pq6": {
                "question": "6. 수술 후 폐에 문제가 생기는 것을 예방하기 위해 어떤 행동이 도움이 될까요?",
                "options": [
                    "움직이지 말고 계속 누워 있기",
                    "말을 적게 하고 조용히 있기",
                    "깊게 숨 쉬기 운동을 하고, 조금씩 자주 움직이기",
                    "얕고 빠르게 숨쉬기 운동하기"
                ],
                "correct": 2,
                "explanation": "깊은 호흡 운동과 조기 보행은 폐 합병증을 예방하는 가장 좋은 방법입니다."
            },
            "pq7": {
                "question": "7. 무통주사(아픈 걸 줄여주는 주사)를 맞을 때 생길 수 있는 일은?",
                "options": [
                    "속이 울렁거리고 어지러울 수 있어요",
                    "갑자기 땀이 나요",
                    "배가 아프고 손이 떨려요",
                    "기침이 멈추지 않아요"
                ],
                "correct": 0,
                "explanation": "무통주사 후에는 속이 울렁거리거나 어지러울 수 있습니다. 이는 정상적인 반응입니다."
            },
            "pq8": {
                "question": "8. 장(창자)이 서로 붙는 걸 '유착'이라고 해요. 유착을 막으려면 어떻게 해야 할까요?",
                "options": [
                    "가만히 누워 있기",
                    "수술 다음 날부터 걷기 운동하기",
                    "음식을 전혀 먹지 않기",
                    "배를 누르면서 운동하기"
                ],
                "correct": 1,
                "explanation": "조기 보행은 장의 움직임을 촉진하여 유착을 예방하는 데 도움이 됩니다."
            }
        }
        
        for q_id, q_data in post_questions_section2.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.post_quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.post_quiz_answers[q_id] = q_data['options'].index(answer)
                
                # 정답을 클릭했을 때만 해설 표시
                if st.session_state.post_quiz_answers[q_id] == q_data['correct']:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ 정답입니다!</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>❌ 틀렸습니다.</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_post_section2"):
                st.session_state.current_section = 0
                st.rerun()
        with col2:
            if st.button("다음", key="next_post_section2"):
                st.session_state.current_section = 2
                st.rerun()
    
    # Ⅲ. 자기결정권 (2문항)
    elif current_section == 2:
        st.markdown("""
        <div class="section-header">
            <h4>Ⅲ. 자기결정권 (2문항)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        post_questions_section3 = {
            "pq9": {
                "question": "9. 수술에 대한 선택은 누가 최종적으로 결정하나요?",
                "options": [
                    "의사",
                    "가족",
                    "환자"
                ],
                "correct": 2,
                "explanation": "수술에 대한 최종 결정은 환자가 내려야 합니다. 의사는 정보를 제공하고 권고할 수 있지만, 최종 선택은 환자의 권리입니다."
            },
            "pq10": {
                "question": "10. 자기결정권에 해당하지 않는 내용은 무엇인가요?",
                "options": [
                    "설명을 듣고 동의한다",
                    "잘 모르니 의료진에게 맡긴다.",
                    "부작용 가능성을 인지한다.",
                    "언제든 수술동의를 철회할 수 있다."
                ],
                "correct": 0,
                "explanation": "자기결정권은 충분한 정보를 바탕으로 스스로 결정하는 것입니다. '잘 모르니 의료진에게 맡긴다'는 것은 자기결정권이 아닙니다."
            }
        }
        
        for q_id, q_data in post_questions_section3.items():
            st.markdown(f"""
            <div class="quiz-box">
                <div class="quiz-question">{q_data['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 답변 상태 확인
            current_answer = st.session_state.post_quiz_answers.get(q_id, None)
            
            answer = st.radio(
                "답변을 선택하세요:",
                q_data['options'],
                key=q_id,
                label_visibility="collapsed",
                index=None if current_answer is None else current_answer
            )
            
            if answer is not None:
                st.session_state.post_quiz_answers[q_id] = q_data['options'].index(answer)
                
                # 정답을 클릭했을 때만 해설 표시
                if st.session_state.post_quiz_answers[q_id] == q_data['correct']:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ 정답입니다!</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>❌ 틀렸습니다.</h4>
                        <p>""" + q_data['explanation'] + """</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", key="prev_post_section3"):
                st.session_state.current_section = 1
                st.rerun()
        with col2:
            if st.button("사후 퀴즈 제출", key="post_quiz_submit"):
                # 점수 계산
                total_questions = 10
                correct_answers = 0
                
                for q_id, q_data in {**post_questions_section1, **post_questions_section2, **post_questions_section3}.items():
                    if st.session_state.post_quiz_answers.get(q_id) == q_data['correct']:
                        correct_answers += 1
                
                score_percentage = (correct_answers / total_questions) * 100
                
                st.session_state.post_quiz_completed = True
                st.session_state.post_quiz_score = score_percentage
                st.session_state.current_section = 0  # 다음 사용자를 위해 초기화
                
                st.success(f"사후 퀴즈가 제출되었습니다! 점수: {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
                
                # 점수에 따른 피드백
                if score_percentage >= 80:
                    st.markdown("""
                    <div class="success-box">
                        <h4>🎉 훌륭합니다!</h4>
                        <p>로봇수술에 대한 이해도가 매우 높습니다. 이제 자신감을 가지고 수술에 임하실 수 있습니다.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif score_percentage >= 60:
                    st.markdown("""
                    <div class="info-box">
                        <h4>👍 잘하셨습니다!</h4>
                        <p>로봇수술에 대한 기본적인 이해를 잘 하셨습니다. 추가 질문이 있으시면 언제든 물어보세요.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <h4>📚 더 공부해보세요</h4>
                        <p>로봇수술에 대한 이해를 더 높이기 위해 정보를 다시 읽어보시거나 질문해보세요.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.rerun()

# 관리자 대시보드
def render_admin_dashboard():
    st.markdown("""
    <div class="section-header">
        <h3>🔧 관리자 대시보드</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 사용자 데이터 저장
    if st.session_state.get('profile_setup_completed', False):
        current_user_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profile": st.session_state.get('user_profile', {}),
            "pre_quiz_answers": st.session_state.get('quiz_answers', {}),
            "post_quiz_answers": st.session_state.get('post_quiz_answers', {}),
            "pre_quiz_completed": st.session_state.get('pre_quiz_completed', False),
            "post_quiz_completed": st.session_state.get('post_quiz_completed', False),
            "post_quiz_score": st.session_state.get('post_quiz_score', 0)
        }
        
        # 중복 방지를 위해 기존 데이터 확인
        if current_user_data not in st.session_state.all_users_data:
            st.session_state.all_users_data.append(current_user_data)
    
    # 탭으로 관리자 기능 구성
    tab1, tab2, tab3 = st.tabs(["📊 전체 통계", "👥 사용자 목록", "📝 상세 답변"])
    
    with tab1:
        st.markdown("""
        <div class="info-box">
            <h4>전체 통계</h4>
        </div>
        """, unsafe_allow_html=True)
        
        total_users = len(st.session_state.all_users_data)
        completed_pre_quiz = sum(1 for user in st.session_state.all_users_data if user.get('pre_quiz_completed', False))
        completed_post_quiz = sum(1 for user in st.session_state.all_users_data if user.get('post_quiz_completed', False))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 사용자 수", total_users)
        
        with col2:
            st.metric("사전 퀴즈 완료", completed_pre_quiz)
        
        with col3:
            st.metric("사후 퀴즈 완료", completed_post_quiz)
        
        with col4:
            if completed_post_quiz > 0:
                avg_score = sum(user.get('post_quiz_score', 0) for user in st.session_state.all_users_data if user.get('post_quiz_completed', False)) / completed_post_quiz
                st.metric("평균 점수", f"{avg_score:.1f}%")
            else:
                st.metric("평균 점수", "N/A")
        
        # 성별 분포
        if total_users > 0:
            gender_data = {}
            for user in st.session_state.all_users_data:
                gender = user.get('profile', {}).get('gender', '미입력')
                gender_data[gender] = gender_data.get(gender, 0) + 1
            
            st.markdown("### 성별 분포")
            for gender, count in gender_data.items():
                percentage = (count / total_users) * 100
                st.write(f"{gender}: {count}명 ({percentage:.1f}%)")
    
    with tab2:
        st.markdown("""
        <div class="info-box">
            <h4>사용자 목록</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.all_users_data:
            for i, user in enumerate(st.session_state.all_users_data):
                with st.expander(f"사용자 {i+1} - {user.get('timestamp', 'N/A')}"):
                    profile = user.get('profile', {})
                    st.write(f"**나이**: {profile.get('age', 'N/A')}")
                    st.write(f"**성별**: {profile.get('gender', 'N/A')}")
                    st.write(f"**교육수준**: {profile.get('education', 'N/A')}")
                    st.write(f"**수술 유형**: {profile.get('medical_experience', 'N/A')}")
                    st.write(f"**사전 퀴즈 완료**: {'✅' if user.get('pre_quiz_completed', False) else '❌'}")
                    st.write(f"**사후 퀴즈 완료**: {'✅' if user.get('post_quiz_completed', False) else '❌'}")
                    if user.get('post_quiz_completed', False):
                        st.write(f"**사후 퀴즈 점수**: {user.get('post_quiz_score', 0):.1f}%")
        else:
            st.write("아직 사용자 데이터가 없습니다.")
    
    with tab3:
        st.markdown("""
        <div class="info-box">
            <h4>상세 답변 분석</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.all_users_data:
            selected_user = st.selectbox(
                "사용자 선택",
                [f"사용자 {i+1} - {user.get('timestamp', 'N/A')}" for i, user in enumerate(st.session_state.all_users_data)],
                key="admin_user_select"
            )
            
            if selected_user:
                user_index = int(selected_user.split()[1]) - 1
                user = st.session_state.all_users_data[user_index]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 사전 퀴즈 답변")
                    pre_answers = user.get('pre_quiz_answers', {})
                    if pre_answers:
                        for q_id, answer in pre_answers.items():
                            st.write(f"**{q_id}**: {answer}번 선택")
                    else:
                        st.write("사전 퀴즈 답변 없음")
                
                with col2:
                    st.markdown("### 사후 퀴즈 답변")
                    post_answers = user.get('post_quiz_answers', {})
                    if post_answers:
                        for q_id, answer in post_answers.items():
                            st.write(f"**{q_id}**: {answer}번 선택")
                    else:
                        st.write("사후 퀴즈 답변 없음")
                
                # 답변 비교
                if pre_answers and post_answers:
                    st.markdown("### 답변 변화 분석")
                    changed_answers = 0
                    for q_id in pre_answers:
                        if q_id in post_answers and pre_answers[q_id] != post_answers[q_id]:
                            changed_answers += 1
                            st.write(f"**{q_id}**: {pre_answers[q_id]}번 → {post_answers[q_id]}번")
                    
                    if changed_answers == 0:
                        st.write("답변 변화 없음")
                    else:
                        st.write(f"총 {changed_answers}개 문항에서 답변 변화")
        else:
            st.write("분석할 사용자 데이터가 없습니다.")
    
    # 데이터 내보내기
    st.markdown("---")
    st.markdown("### 데이터 내보내기")
    
    if st.button("CSV 파일로 내보내기", key="export_csv"):
        import pandas as pd
        
        # 데이터를 DataFrame으로 변환
        export_data = []
        for user in st.session_state.all_users_data:
            profile = user.get('profile', {})
            row = {
                'timestamp': user.get('timestamp', ''),
                'age': profile.get('age', ''),
                'gender': profile.get('gender', ''),
                'education': profile.get('education', ''),
                'medical_experience': profile.get('medical_experience', ''),
                'pre_quiz_completed': user.get('pre_quiz_completed', False),
                'post_quiz_completed': user.get('post_quiz_completed', False),
                'post_quiz_score': user.get('post_quiz_score', 0)
            }
            
            # 퀴즈 답변 추가
            pre_answers = user.get('pre_quiz_answers', {})
            post_answers = user.get('post_quiz_answers', {})
            
            for q_id in range(1, 11):
                row[f'pre_q{q_id}'] = pre_answers.get(f'q{q_id}', '')
                row[f'post_q{q_id}'] = post_answers.get(f'pq{q_id}', '')
            
            export_data.append(row)
        
        if export_data:
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV 다운로드",
                data=csv,
                file_name=f"robot_surgery_quiz_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("내보낼 데이터가 없습니다.")

# 메인 페이지
def render_main_page():
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="color: #4CAF50; font-size: 2.5rem; margin-bottom: 1rem;">🤖 로봇수술동의서 이해증진도구</h1>
        <p style="color: #666; font-size: 1.2rem;">로봇수술에 대한 이해를 높이는 교육 도구</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-header">
        <h3>🏠 메인 페이지</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>환영합니다!</h4>
        <p>로봇수술동의서 이해증진도구에 오신 것을 환영합니다. 
        사이드바의 메뉴를 통해 원하시는 기능을 선택하실 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
            <h4>📝 사전 퀴즈</h4>
            <p>로봇수술에 대한 현재 이해도를 평가해보세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("사전 퀴즈 시작", key="main_pre_quiz"):
            st.session_state.current_page = "pre_quiz"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>📚 로봇수술 정보</h4>
            <p>로봇수술에 대한 자세한 정보를 확인하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("정보 보기", key="main_info"):
            st.session_state.current_page = "info"
            st.rerun()
    
    # 사전 퀴즈가 완료된 경우에만 사후 퀴즈 표시
    if st.session_state.get('pre_quiz_completed', False):
        st.markdown("""
        <div class="success-box">
            <h4>📊 사후 퀴즈</h4>
            <p>로봇수술 정보를 학습한 후 이해도를 평가해보세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("사후 퀴즈 시작", key="main_post_quiz"):
            st.session_state.current_page = "post_quiz"
            st.rerun()
    
    st.markdown("""
    <div class="warning-box">
        <h4>💬 질문하기</h4>
        <p>로봇수술에 대해 궁금한 점이 있으시면 AI 상담사에게 질문하세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("질문하기", key="main_chat"):
        st.session_state.current_page = "chat"
        st.rerun()

# 메인 콘텐츠
def render_main_content():
    st.markdown("""
    <div class="section-header">
        <h3>📚 로봇수술 정보</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭으로 정보 구성
    tab1, tab2, tab3, tab4 = st.tabs(["로봇수술이란?", "수술에서 무슨 일이?", "수술 후 관리는?", "동의서가 중요한가요?"])
    
    with tab1:
        st.markdown("""
        <div class="info-box">
            <h4>로봇수술이란?</h4>
            <p>로봇수술은 의료진이 컴퓨터 콘솔을 통해 로봇 팔을 조작하여 수술을 수행하는 최첨단 수술 방법입니다. 
            다빈치 수술 로봇이 가장 널리 사용되고 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **주요 특징:**
        - 3D 고화질 영상으로 수술 부위를 확대해서 볼 수 있음
        - 로봇 팔의 정밀한 움직임으로 미세한 수술 가능
        - 의료진의 손떨림을 자동으로 보정
        - 최소 절개로 수술 가능
        """)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="success-box">
                <h4>✅ 장점</h4>
                <ul>
                    <li>정밀도와 안정성</li>
                    <li>최소 절개</li>
                    <li>빠른 회복</li>
                    <li>적은 출혈</li>
                    <li>감염 위험 감소</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ 단점</h4>
                <ul>
                    <li>높은 비용</li>
                    <li>장비 의존성</li>
                    <li>의료진 교육 필요</li>
                    <li>수술 시간 연장 가능</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        **수술 과정:**
        1. **마취**: 전신마취 또는 척추마취
        2. **체위 설정**: 수술에 적합한 자세로 배치
        3. **로봇 배치**: 로봇 팔을 수술 부위에 위치
        4. **수술 수행**: 의료진이 콘솔에서 로봇 조작
        5. **수술 완료**: 로봇 제거 및 상처 봉합
        """)
    
    with tab4:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ 주의사항</h4>
            <ul>
                <li>모든 수술에는 위험이 따릅니다</li>
                <li>개인별 차이로 결과가 다를 수 있습니다</li>
                <li>수술 후 합병증 가능성이 있습니다</li>
                <li>의료진과 충분한 상담이 필요합니다</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 챗봇 기능
def render_chatbot():
    st.markdown("""
    <div class="section-header">
        <h3>💬 질문하기</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>AI 상담사</h4>
        <p>로봇수술에 대해 궁금한 점이 있으시면 언제든 질문해 주세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 채팅 히스토리 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하고 있습니다..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "당신은 로봇수술 전문 상담사입니다. 친절하고 정확한 정보를 제공해 주세요."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    ai_response = response.choices[0].message.content
                    st.write(ai_response)
                    
                    # AI 응답을 히스토리에 추가
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    st.error(f"응답 생성 중 오류가 발생했습니다: {str(e)}")

# 메인 앱 실행
def main():
    # 사이드바 네비게이션 렌더링
    render_sidebar_navigation()
    
    # 프로필 설정이 완료되지 않은 경우
    if not st.session_state.get('profile_setup_completed', False):
        render_profile_setup()
        return
    
    # 사전 퀴즈가 완료되지 않은 경우
    if not st.session_state.get('pre_quiz_completed', False):
        render_pre_quiz()
        return
    
    # 현재 페이지에 따른 콘텐츠 표시
    if st.session_state.current_page == "main":
        render_main_page()
    elif st.session_state.current_page == "pre_quiz":
        render_pre_quiz()
    elif st.session_state.current_page == "info":
        render_main_content()
    elif st.session_state.current_page == "post_quiz":
        render_post_quiz()
    elif st.session_state.current_page == "chat":
        render_chatbot()
    elif st.session_state.current_page == "admin":
        render_admin_dashboard()
    else:
        render_main_content()
    
    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 1rem;">
        <p>이 도구는 교육 목적으로 제작되었습니다. 실제 의료 상담은 전문 의료진과 상담하세요.</p>
        <p>© 2024 로봇수술동의서 이해증진도구</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
