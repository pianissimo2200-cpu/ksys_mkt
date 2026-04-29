import time
import os
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import collector_utils as utils
import ai_utils

# --- 커스텀 스타일 정의 (Toss/Apple Style) ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* Pretendard 폰트 로드 */
        @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css");
        
        html, body, [class*="css"], .stMarkdown, p {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
        }
        
        /* 스트림릿 기본 요소 대비 강화 및 텍스트 강제 고정 */
        .stMarkdown p, .stMarkdown div, .stMarkdown span, .stMetric div, .stRadio label {
            color: #191F28 !important;
        }

        /* 배경색 설정 */
        .stApp {
            background-color: #F2F4F7;
        }

        /* 카드 스타일 */
        .content-card {
            background-color: #FFFFFF;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
            margin-bottom: 1.5rem;
        }

        /* 제목 스타일 */
        h1, h2, h3 {
            color: #191F28 !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        /* 사이드바 스타일 */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E5E8EB !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown h1 {
            font-size: 1.5rem !important;
            margin-bottom: 2rem !important;
        }

        /* 버튼 스타일 (미니멀 & 직관적) */
        div[data-testid="stAppViewContainer"] .stButton>button[kind="primary"] {
            background-color: #3182F6 !important; /* 토스 블루 */
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            width: 100%;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(0, 100, 255, 0.1);
        }
        div[data-testid="stAppViewContainer"] .stButton>button[kind="primary"]:hover {
            background-color: #1B64DA !important;
            box-shadow: 0 4px 12px rgba(49, 130, 246, 0.2) !important;
            transform: translateY(-1px);
        }
        
        /* 입력창 스타일 */
        .stTextInput>div>div>input {
            border-radius: 10px !important;
            border: 1px solid #E5E8EB !important;
            padding: 0.8rem 1rem !important;
        }

        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: white;
            border-radius: 10px;
            padding: 0 20px;
            border: 1px solid #E5E8EB;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0064FF !important;
            color: white !important;
            border: 1px solid #0064FF !important;
        }

        /* 키워드 관리 행 스타일 (간격 축소 및 Hover 효과) */
        .keyword-row {
            display: flex;
            align-items: center;
            padding: 2px 8px;
            margin: 2px 0;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        .keyword-row:hover {
            background-color: #F2F4F7;
        }
        
        /* 삭제 버튼 및 즐겨찾기 버튼 공통 스타일 */
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
            opacity: 0 !important;
            width: 22px !important;
            height: 22px !important;
            min-height: 22px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            background-color: transparent !important;
            color: transparent !important;
            border: none !important;
            font-size: 12px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* 키워드 행에 마우스 올렸을 때 버튼들 노출 */
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover button {
            opacity: 1 !important;
            background-color: #F2F4F7 !important;
            color: #8B95A1 !important;
        }
        
        /* 삭제 버튼 전용 (두 번째 버튼) 호버 시 빨간색 */
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div:nth-child(3) button:hover {
            background-color: #FF4B4B !important;
            color: white !important;
        }

        /* 즐겨찾기 버튼 전용 (첫 번째 버튼) 호버 시 노란색 */
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div:nth-child(2) button:hover {
            background-color: #FFD400 !important;
            color: #191F28 !important;
        }

        /* 즐겨찾기 버튼이 활성화된 경우(노란색 별표) 시각적 피드백 강화 */
        section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[aria-label="★"] {
            opacity: 1 !important;
            color: #FFD400 !important;
        }

        /* 테이블 내부 스크롤 제거를 위한 스타일 */
        .modern-table-container {
            width: 100%;
            overflow-x: visible !important;
            overflow-y: visible !important;
        }
        .modern-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 10px;
            border-radius: 12px;
            border: 1px solid #F2F4F7;
        }
        .modern-table th {
            background-color: #F9FAFB;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            color: #4E5968;
            border-bottom: 1px solid #F2F4F7;
        }
        .modern-table td {
            padding: 14px 16px;
            border-bottom: 1px solid #F2F4F7;
            color: #191F28;
            vertical-align: middle;
            font-size: 14px;
        }
        .modern-table td a {
            color: #191F28;
            text-decoration: none;
            transition: color 0.2s ease;
        }
        .modern-table td a:hover {
            color: #0064FF !important;
            text-decoration: underline !important;
        }

        /* 메트릭(KPI) 대비 강화 */
        [data-testid="stMetricValue"] div {
            color: #191F28 !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] p {
            color: #4E5968 !important;
            font-weight: 500 !important;
        }

        /* 라디오 버튼(메뉴) 대비 강화 */
        div[data-testid="stRadio"] label p {
            color: #191F28 !important;
            font-weight: 500 !important;
        }

        /* 메트릭(KPI) 스타일 */
        [data-testid="stMetric"] {
            background-color: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            border: 1px solid #F2F4F7;
        }
        
        /* 배지 스타일 */
        .badge {
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
            white-space: nowrap;
        }
        .badge-green { background-color: #E6F4F1 !important; color: #008485 !important; }
        .badge-red { background-color: #FEEBEB !important; color: #E91E63 !important; }
        .badge-yellow { background-color: #FFF8E1 !important; color: #FF8F00 !important; }

        /* 비밀번호 컨테이너 */
        .login-box {
            max-width: 450px;
            margin: 100px auto;
            padding: 50px;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.05);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sortable_html_table(df_display, classes='modern-table'):
    """HTML 테이블에 CSS와 정렬 기능을 위한 JS를 삽입하여 반환합니다."""
    table_html = df_display.to_html(escape=False, index=False, classes=classes)
    
    css = """
    <style>
        @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css");
        body { font-family: 'Pretendard', sans-serif; margin: 0; padding: 0; background-color: transparent; }
        .modern-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; border: 1px solid #F2F4F7; }
        .modern-table th { background-color: #F9FAFB; padding: 12px 16px; text-align: left; font-weight: 600; color: #4E5968; border-bottom: 1px solid #F2F4F7; cursor: pointer; user-select: none; transition: background-color 0.2s; }
        .modern-table th:hover { background-color: #E5E8EB; }
        .modern-table td { padding: 14px 16px; border-bottom: 1px solid #F2F4F7; color: #191F28; vertical-align: middle; font-size: 14px; }
        .modern-table td a { color: #191F28; text-decoration: none; transition: color 0.2s ease; }
        .modern-table td a:hover { color: #0064FF; text-decoration: underline; }
        .badge { padding: 4px 12px; border-radius: 50px; font-size: 12px; font-weight: 600; display: inline-block; white-space: nowrap; }
        .badge-green { background-color: #E6F4F1; color: #008485; }
        .badge-red { background-color: #FEEBEB; color: #E91E63; }
        .badge-yellow { background-color: #FFF8E1; color: #FF8F00; }
    </style>
    """
    
    js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const table = document.querySelector('.modern-table');
        const ths = table.querySelectorAll('th');
        ths.forEach((th, idx) => {
            th.title = '클릭하여 정렬';
            th.onclick = function() {
                const asc = this.asc = !this.asc;
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    const v1 = a.children[idx].innerText.trim();
                    const v2 = b.children[idx].innerText.trim();
                    
                    // 1. 날짜 파싱 시도
                    const d1 = Date.parse(v1.replace(' ', 'T'));
                    const d2 = Date.parse(v2.replace(' ', 'T'));
                    if (!isNaN(d1) && !isNaN(d2)) return asc ? d1 - d2 : d2 - d1;
                    
                    // 2. 숫자 파싱 시도 (순위 등)
                    const n1 = parseFloat(v1.replace(/[^0-9.-]+/g,''));
                    const n2 = parseFloat(v2.replace(/[^0-9.-]+/g,''));
                    if (!isNaN(n1) && !isNaN(n2)) return asc ? n1 - n2 : n2 - n1;
                    
                    // 3. 문자열 비교
                    return asc ? v1.localeCompare(v2) : v2.localeCompare(v1);
                });
                
                rows.forEach(tr => tbody.appendChild(tr));
                ths.forEach(h => h.innerHTML = h.innerHTML.replace(/ [▲▼]/g, ''));
                this.innerHTML += asc ? ' ▲' : ' ▼';
            };
        });
    });
    </script>
    """
    return f"<!DOCTYPE html><html><head>{css}</head><body>{table_html}{js}</body></html>"

# 환경 변수 로드 (.env)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
COMPANY_NAME = os.environ.get("COMPANY_NAME", "케이시스")

# 네이버 API 키 설정 (os.environ 사용)
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")
SA_API_KEY = os.environ.get("SA_API_KEY", "")
SA_SECRET_KEY = os.environ.get("SA_SECRET_KEY", "")
SA_CUSTOMER_ID = os.environ.get("SA_CUSTOMER_ID", "")

# 유틸리티 함수 래핑 및 캐싱 (API 한도 초과 방지 및 속도 향상)
@st.cache_data(ttl=600, show_spinner=False)
def load_competitors():
    return utils.load_competitors()

def save_competitors(data):
    utils.save_competitors(data)
    load_competitors.clear()

@st.cache_data(ttl=600, show_spinner=False)
def load_keywords():
    return utils.load_keywords()

def save_keywords(data):
    utils.save_keywords(data)
    load_keywords.clear()

@st.cache_data(ttl=600, show_spinner=False)
def load_rank_keywords():
    return utils.load_rank_keywords()

def save_rank_keywords(data):
    utils.save_rank_keywords(data)
    load_rank_keywords.clear()

@st.cache_data(ttl=600, show_spinner=False)
def load_trend_keywords():
    return utils.load_trend_keywords()

def save_trend_keywords(data):
    utils.save_trend_keywords(data)
    load_trend_keywords.clear()

fetch_blog_feed = utils.fetch_blog_feed

def fetch_naver_news(query, start_date, end_date):
    return utils.fetch_naver_news(query, start_date, end_date, CLIENT_ID, CLIENT_SECRET)

def fetch_naver_rank(query, search_target=None):
    if search_target is None:
        search_target = COMPANY_NAME
    return utils.fetch_naver_rank(query, CLIENT_ID, CLIENT_SECRET, search_target)

def fetch_naver_search_volume(keyword):
    return utils.fetch_naver_search_volume(keyword, SA_API_KEY, SA_SECRET_KEY, SA_CUSTOMER_ID)

def fetch_naver_datalab_trend(keywords, start_date, end_date, gender=None, ages=None, time_unit='month'):
    return utils.fetch_naver_datalab_trend(keywords, start_date, end_date, CLIENT_ID, CLIENT_SECRET, time_unit=time_unit, gender=gender, ages=ages)

def get_secret(key, default=""):
    """st.secrets에서 값을 안전하게 가져옵니다. 로컬 환경에서 secrets.toml이 없을 때의 에러를 방지합니다."""
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default

def check_password():
    """비밀번호가 맞는지 확인합니다. 맞으면 True, 틀리면 로그인 화면을 출력합니다."""
    def password_entered():
        # Secrets에 설정이 없으면 'ksys1234'를 기본 비밀번호로 사용
        correct_password = get_secret("APP_PASSWORD", "ksys1234")
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 보안을 위해 세션에서 비밀번호 삭제
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 로그인 화면 중앙 정렬을 위한 컬럼 배치
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            # 카드 느낌을 주기 위한 컨테이너 스타일링
            st.markdown("""
                <div style='text-align: center; padding: 40px; background: white; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.05);'>
                    <h1 style='font-size: 50px; margin-bottom: 10px;'>📈</h1>
                    <h2 style='color: #191F28; margin-bottom: 30px;'>마케팅 인사이트</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # 입력창 (위 카드 바로 아래에 배치)
            password = st.text_input("비밀번호", type="password", key="password_input", placeholder="접속 비밀번호를 입력하세요", label_visibility="collapsed")
            if st.button("로그인", use_container_width=True, type="primary"):
                correct_password = get_secret("APP_PASSWORD", "ksys1234")
                if password == correct_password:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("😕 비밀번호가 틀렸습니다.")
            
            st.markdown('<p style="text-align: center; color: #8B95A1; font-size: 14px; margin-top: 30px;">© 2026 KSYS Marketing Team</p>', unsafe_allow_html=True)
        return False
    return True

def main():
    st.set_page_config(page_title="마케팅 인사이트 대시보드", page_icon="📈", layout="wide")
    
    inject_custom_css()
    
    if not check_password():
        st.stop()
    
    # API 키 초기 로드 (함수 최상단에서 선언하여 에러 방지)
    st.session_state['gemini_key'] = os.environ.get("GEMINI_API_KEY", get_secret("GEMINI_API_KEY", ""))
    st.session_state['openai_key'] = os.environ.get("OPENAI_API_KEY", get_secret("OPENAI_API_KEY", ""))

    # 크롬 브라우저 자동번역 방지 스크립트
    st.components.v1.html(
        """<script>window.parent.document.documentElement.lang = 'ko';window.parent.document.body.setAttribute('translate', 'no');</script>""",
        height=0, width=0
    )
    
    # 데이터 로드 및 즐겨찾기 기반 정렬
    def sort_by_fav(items):
        if not items: return []
        # 문자열 리스트인 경우와 딕셔너리 리스트인 경우 모두 대응
        def get_sort_key(x):
            is_fav = x.get('fav', False) if isinstance(x, dict) else False
            name = x.get('name', str(x)) if isinstance(x, dict) else str(x)
            return (not is_fav, name)
        
        return sorted(items, key=get_sort_key)

    competitors = sort_by_fav(load_competitors())
    keywords = sort_by_fav(load_keywords())
    rank_keywords = sort_by_fav(load_rank_keywords())
    trend_keywords = sort_by_fav(load_trend_keywords())
    
    # --- 메인 화면 상단 ---
    st.markdown("# 마케팅 인사이트 대시보드")
    
    menu_options = ["뉴스 통합 브리핑", "경쟁사 포스팅 분석", "네이버 상위노출 추적", "검색 트렌드 분석", "키워드 선점 추천"]
    selected_menu = st.radio("메뉴 선택", menu_options, horizontal=True, label_visibility="collapsed", key="main_menu_v3")
    
    # --- 사이드바 영역 (미니멀 & 점진적 노출) ---
    with st.sidebar:
        st.markdown("# 설정")
        
        # 1. 수집 기간 설정
        st.markdown("### 수집 기간")
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        date_range = st.date_input("조회 기간", value=(one_week_ago, today), max_value=today, label_visibility="collapsed")
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]
        else:
            start_date, end_date = today, today

        st.divider()
        
        # 메뉴에 따른 키워드 관리 노출 (점진적 정보 공개)
        # 메뉴에 따른 키워드 관리 노출 (점진적 정보 공개)
        def render_keyword_management(title, kws, save_func, key_prefix):
            with st.expander(title, expanded=True):
                new_k = st.text_input(f"{title} 추가", key=f"add_{key_prefix}")
                if st.button(f"{title} 저장", type="primary", use_container_width=True, key=f"save_{key_prefix}"):
                    if new_k:
                        # 중복 체크 (문자열 리스트와의 호환성 고려)
                        exists = any((k['name'] if isinstance(k, dict) else k) == new_k for k in kws)
                        if not exists:
                            kws.append({"name": new_k, "fav": False})
                            save_func(kws)
                            st.rerun()

                # 키워드 데이터 구조 정규화 (문자열 -> 딕셔너리) 및 정렬
                # 정렬 기준: 1. 즐겨찾기(True가 위로), 2. 이름순
                normalized_kws = []
                for k in kws:
                    if isinstance(k, dict):
                        normalized_kws.append(k)
                    else:
                        normalized_kws.append({"name": str(k), "fav": False})
                
                sorted_kws = sorted(
                    normalized_kws, 
                    key=lambda x: (not x.get('fav', False), x.get('name', ''))
                )

                for i, k in enumerate(sorted_kws):
                    name = k['name']
                    is_fav = k.get('fav', False)
                    
                    c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
                    c1.markdown(f"<div style='padding: 2px 0; font-size: 14px;'>• {name}</div>", unsafe_allow_html=True)
                    
                    # 즐겨찾기 버튼
                    fav_icon = "★" if is_fav else "☆"
                    if c2.button(fav_icon, key=f"fav_{key_prefix}_{i}", help="즐겨찾기 등록/해제"):
                        # 원본 리스트에서 해당 키워드 찾아 상태 반전
                        for orig_k in kws:
                            if isinstance(orig_k, dict) and orig_k['name'] == name:
                                orig_k['fav'] = not orig_k.get('fav', False)
                                break
                            elif not isinstance(orig_k, dict) and str(orig_k) == name:
                                # 문자열인 경우 찾아서 딕셔너리로 교체
                                idx = kws.index(orig_k)
                                kws[idx] = {"name": name, "fav": True}
                                break
                        save_func(kws)
                        st.rerun()
                    
                    # 삭제 버튼
                    if c3.button("X", key=f"del_{key_prefix}_{i}", help="삭제"):
                        # 원본 리스트에서 삭제
                        for orig_k in kws:
                            if (isinstance(orig_k, dict) and orig_k['name'] == name) or (not isinstance(orig_k, dict) and str(orig_k) == name):
                                kws.remove(orig_k)
                                break
                        save_func(kws)
                        st.rerun()

        if selected_menu == "뉴스 통합 브리핑":
            render_keyword_management("🔑 뉴스 키워드 관리", keywords, save_keywords, "nw")

        elif selected_menu == "경쟁사 포스팅 분석":
            with st.expander("🏢 경쟁사 블로그 관리", expanded=True):
                new_name = st.text_input("업체명", key="add_comp")
                new_url = st.text_input("블로그URL", key="add_comp_url")
                if st.button("경쟁사 등록", type="primary", use_container_width=True, key="save_comp"):
                    if new_name and new_url:
                        # 중복 체크
                        if not any(c['url'] == new_url for c in competitors):
                            competitors.append({"name": new_name, "url": new_url, "fav": False})
                            save_competitors(competitors)
                            st.rerun()
                
                # 경쟁사 정렬 (즐겨찾기 우선)
                sorted_comps = sorted(
                    competitors,
                    key=lambda x: (not x.get('fav', False), x.get('name', ''))
                )

                for i, comp in enumerate(sorted_comps):
                    name = comp['name']
                    is_fav = comp.get('fav', False)
                    
                    c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
                    c1.markdown(f"<div style='padding: 2px 0; font-size: 14px;'>• {name}</div>", unsafe_allow_html=True)
                    
                    # 즐겨찾기 버튼
                    fav_icon = "★" if is_fav else "☆"
                    if c2.button(fav_icon, key=f"fav_comp_{i}", help="즐겨찾기"):
                        for orig_c in competitors:
                            if orig_c['url'] == comp['url']:
                                orig_c['fav'] = not orig_c.get('fav', False)
                                break
                        save_competitors(competitors)
                        st.rerun()
                    
                    # 삭제 버튼
                    if c3.button("X", key=f"del_comp_v2_{i}", help="삭제"):
                        for orig_c in competitors:
                            if orig_c['url'] == comp['url']:
                                competitors.remove(orig_c)
                                break
                        save_competitors(competitors)
                        st.rerun()

        elif selected_menu == "네이버 상위노출 추적":
            render_keyword_management("상위노출 키워드 관리", rank_keywords, save_rank_keywords, "rk")

        elif selected_menu == "검색 트렌드 분석":
            render_keyword_management("트렌드 키워드 관리", trend_keywords, save_trend_keywords, "tk")

        st.divider()
        # 구글 시트 연동 상태 표시
        if utils.check_gsheet_connection():
            st.success("✅ 구글 시트 연동 중")
        else:
            st.error("❌ 구글 시트 연결 실패")
            if st.button("재시도"):
                st.rerun()

    # --- 상단 요약 지표 (Summary Metrics) ---
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("뉴스 키워드", f"{len(keywords)}개")
    m2.metric("경쟁사 블로그", f"{len(competitors)}개")
    m3.metric("상위노출 추적", f"{len(rank_keywords)}개")
    m4.metric("수집 기간", f"{(end_date - start_date).days}일")
    st.markdown("<br>", unsafe_allow_html=True)

    # ===== 메뉴별 화면 렌더링 =====
    if selected_menu == "뉴스 통합 브리핑":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("뉴스 통합 브리핑")
        if st.button("뉴스 수집 시작", type="primary", use_container_width=True, key="news_fetch_btn"):
            if not CLIENT_ID or not CLIENT_SECRET:
                st.error("❌ 네이버 API 키가 설정되지 않았습니다. Streamlit Secrets에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 등록해 주세요.")
            else:
                with st.spinner("뉴스를 수집하는 중입니다..."):
                    all_news = []
                    # 키워드 데이터 구조 호환성 처리 (객체 리스트 -> 문자열 리스트)
                    kw_list = [k['name'] if isinstance(k, dict) else k for k in keywords]
                    for kw in kw_list:
                        df = fetch_naver_news(kw, start_date, end_date)
                        if not df.empty:
                            df.insert(0, '키워드', kw)
                            all_news.append(df)
                    if all_news:
                        st.session_state['latest_news_df'] = pd.concat(all_news)
                    else:
                        st.session_state['latest_news_df'] = pd.DataFrame()
                        st.info("해당 기간 동안 검색된 뉴스가 없습니다.")

        if 'latest_news_df' in st.session_state and not st.session_state['latest_news_df'].empty:
            df = st.session_state['latest_news_df'].copy()
            
            # 발행일 컬럼 기본 정렬 (최신순)
            if '발행일' in df.columns:
                df = df.sort_values(by='발행일', ascending=False)
                        
            # 제목을 클릭 가능한 링크로 변환하고 링크 컬럼 제거
            def make_title_clickable(row):
                return f'<a href="{row["링크"]}" target="_blank" style="text-decoration:none; color:#191F28; font-weight:600;">{row["제목"]}</a>'
            
            df['제목'] = df.apply(make_title_clickable, axis=1)
            df_display = df[['키워드', '제목', '언론사', '발행일']].copy()
            
            html_content = render_sortable_html_table(df_display)
            calc_height = len(df_display) * 48 + 50
            st.components.v1.html(html_content, height=calc_height, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    elif selected_menu == "경쟁사 포스팅 분석":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("경쟁사 최신 포스팅 분석 및 AI 콘텐츠 어시스턴트")
        
        with st.expander("AI 콘텐츠 생성 설정 (API 키 및 자사 정보)", expanded=False):
            st.markdown("경쟁사 블로그 본문을 분석하고 AI가 글과 이미지를 자동 생성하기 위해 설정이 필요합니다.")
            
            c1, c2 = st.columns([0.8, 0.2])
            st.session_state['gemini_key'] = c1.text_input("Gemini API Key", type="password", value=st.session_state['gemini_key'])
            if c2.button("Gemini 키 확인", use_container_width=True):
                is_valid, msg = ai_utils.validate_gemini_key(st.session_state['gemini_key'])
                if is_valid: st.success(f"✅ {msg}")
                else: st.error(f"❌ {msg}")
            
            c3, c4 = st.columns([0.8, 0.2])
            st.session_state['openai_key'] = c3.text_input("OpenAI API Key", type="password", value=st.session_state['openai_key'])
            if c4.button("OpenAI 키 확인", use_container_width=True):
                is_valid, msg = ai_utils.validate_openai_key(st.session_state['openai_key'])
                if is_valid: st.success(f"✅ {msg}")
                else: st.error(f"❌ {msg}")
                    
            company_positioning = st.text_area("자사 기본 정보 및 강조할 강점", 
                                             value="우리는 우수한 기술력과 합리적인 가격, 그리고 신속한 사후 관리를 제공합니다.",
                                             placeholder="예: 우리는 10년 경력의 설치 노하우가 있고, 가격 경쟁력이 뛰어나며 24시간 AS를 지원합니다.")
            
        st.markdown("### 🔍 경쟁사 최신 포스팅 수집")
        if st.button("경쟁사 포스팅 가져오기", type="primary", use_container_width=True):
            all_blogs = []
            with st.spinner("경쟁사 블로그 수집 중..."):
                for comp in competitors:
                    posts = fetch_blog_feed(comp['url'], start_date, end_date)
                    for p in posts:
                        p['업체명'] = comp['name']
                        all_blogs.append(p)
            if all_blogs:
                st.session_state['latest_blogs'] = all_blogs
                st.success(f"총 {len(all_blogs)}개의 포스팅을 발견했습니다.")
            else:
                st.session_state['latest_blogs'] = []
                st.info("해당 기간 내 수집된 포스팅이 없습니다.")

        if 'latest_blogs' in st.session_state and st.session_state['latest_blogs']:
            blogs_df = pd.DataFrame(st.session_state['latest_blogs'])
            
            if '발행일' in blogs_df.columns:
                blogs_df = blogs_df.sort_values(by='발행일', ascending=False)
            
            # 제목을 클릭 가능한 링크로 변환하고 링크 컬럼 제거
            def make_comp_title_clickable(row):
                return f'<a href="{row["링크"]}" target="_blank" style="text-decoration:none; color:#191F28; font-weight:600;">{row["제목"]}</a>'
            
            blogs_df['제목'] = blogs_df.apply(make_comp_title_clickable, axis=1)
            df_display = blogs_df[['업체명', '발행일', '제목']].copy()
            
            html_content = render_sortable_html_table(df_display)
            calc_height = len(df_display) * 48 + 50
            st.components.v1.html(html_content, height=calc_height, scrolling=False)
            
            st.divider()
            st.markdown("### 🤖 분석 및 콘텐츠 자동 생성")
            col_sel, col_opt, col_btn = st.columns([0.4, 0.3, 0.3])
            
            blog_list = st.session_state['latest_blogs']
            titles = [f"[{b['업체명']}] {b['제목']}" for b in blog_list]
            selected_title = col_sel.selectbox("분석할 포스팅 선택", titles)
            selected_post = blog_list[titles.index(selected_title)]
            
            with col_opt:
                ai_model = st.radio("사용할 AI 모델", ["Gemini (1.5 Flash)", "GPT (4o)"], horizontal=True)
                gen_option = st.radio("생성 범위", ["글만 생성", "이미지만 생성", "글 + 이미지 모두 생성"], horizontal=True)
            
            if col_btn.button("✨ 콘텐츠 생성 시작", use_container_width=True):
                m_type = 'gemini' if "Gemini" in ai_model else 'gpt'
                target_key = st.session_state['gemini_key'] if m_type == 'gemini' else st.session_state['openai_key']
                
                if not target_key and ("글" in gen_option or "모두" in gen_option):
                    st.error(f"텍스트 생성을 위해 {m_type.upper()} API Key를 입력해주세요.")
                elif not openai_key and ("이미지" in gen_option or "모두" in gen_option):
                    st.error("이미지 생성을 위해 OpenAI API Key를 입력해주세요.")
                else:
                    with st.spinner("경쟁사 블로그 본문을 스크래핑하는 중..."):
                        full_content = utils.fetch_blog_full_content(selected_post['링크'])
                    
                    if not full_content:
                        st.error("본문 스크래핑에 실패했습니다. (네이버 블로그 본문만 지원됩니다)")
                    else:
                        col_l, col_r = st.columns(2)
                        with col_l:
                            with st.expander("📝 원본 내용 보기", expanded=False):
                                st.text_area("원본 본문", full_content[:1500] + "\n\n... (이하 생략)", height=400, disabled=True)
                        
                        with col_r:
                            st.markdown(f"##### 🤖 {ai_model} 생성 결과")
                            topic_summary = selected_post['제목']
                            
                            # 텍스트 생성
                            if "글" in gen_option or "모두" in gen_option:
                                with st.spinner(f"{ai_model}가 분석 및 작성 중..."):
                                    generated_text = ai_utils.analyze_and_generate_post(full_content, company_positioning, target_key, model_type=m_type)
                                    st.markdown(generated_text)
                                    st.download_button("📝 텍스트 다운로드", data=generated_text, file_name=f"generated_post_{m_type}.md", mime="text/markdown")
                                    topic_summary = generated_text[:200].replace('#', '').replace('*', '')
                            
                            # 이미지 생성
                            if "이미지" in gen_option or "모두" in gen_option:
                                with st.spinner("DALL-E 3가 썸네일 이미지를 생성하는 중..."):
                                    img_url, img_err = ai_utils.generate_blog_image(topic_summary, st.session_state['openai_key'])
                                    if img_err:
                                        st.error(img_err)
                                    elif img_url:
                                        st.image(img_url, caption="생성된 AI 썸네일", use_container_width=True)
                                        st.markdown(f"[🔗 이미지 원본 다운로드]({img_url})")
        st.markdown('</div>', unsafe_allow_html=True)

    elif selected_menu == "검색 트렌드 분석":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📊 키워드 검색 트렌드 분석")
        if not trend_keywords:
            st.info("👈 좌측에서 트렌드 분석 키워드를 추가해 주세요.")
        else:
            sc1, sc2 = st.columns([0.3, 0.7])
            t_unit = sc1.selectbox("분석 단위", ["date", "week", "month"], index=2)
            d_range = sc2.date_input("분석 기간", value=(datetime.date.today()-datetime.timedelta(days=365), datetime.date.today()))
            
            show_absolute = st.toggle("절대 검색량(추정)으로 보기", value=True)
            if st.button("분석 실행", type="primary", use_container_width=True):
                if len(d_range) == 2:
                    # 키워드 리스트 정규화
                    kw_list = [k['name'] if isinstance(k, dict) else k for k in trend_keywords]
                    df_nv = fetch_naver_datalab_trend(kw_list, d_range[0].strftime("%Y-%m-%d"), d_range[1].strftime("%Y-%m-%d"), time_unit=t_unit)
                    if not df_nv.empty:
                        if show_absolute:
                            for kw in kw_list:
                                vol = fetch_naver_search_volume(kw)
                                max_ratio = df_nv[df_nv['키워드'] == kw]['트렌드지수'].max()
                                scaler = vol['total'] / (max_ratio if max_ratio > 0 else 1)
                                df_nv.loc[df_nv['키워드'] == kw, '표시수치'] = df_nv['트렌드지수'] * scaler
                        else:
                            df_nv['표시수치'] = df_nv['트렌드지수']
                        
                        fig = px.line(df_nv, x='날짜', y='표시수치', color='키워드', markers=True, template='plotly_white')
                        fig.update_layout(
                            font_family="Pretendard",
                            hovermode="x unified",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=30, b=0),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        fig.update_traces(line_width=3, marker=dict(size=8))
                        st.plotly_chart(fig, use_container_width=True)
                        st.download_button("📊 CSV 다운로드", data=df_nv.to_csv(index=False).encode('utf-8'), file_name="trend_analysis.csv")
                else:
                    st.warning("기간을 시작일과 종료일 모두 선택해주세요.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif selected_menu == "🏆 네이버 상위노출 현황":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("🏆 네이버 통합검색 상위노출 현황")
        if not rank_keywords:
            st.info("👈 좌측 설정에서 상위노출을 확인할 키워드를 관리해주세요.")
        else:
            target_name = st.text_input("추적할 업체/브랜드명 (미입력 시 자사명)", value=COMPANY_NAME)
            if st.button("순위 추적 시작", type="primary", use_container_width=True):
                if not CLIENT_ID or not CLIENT_SECRET:
                    st.error("❌ 네이버 API 키가 설정되지 않았습니다. Streamlit Secrets 설정을 확인해 주세요.")
                else:
                    with st.spinner("상위노출 순위를 조회하는 중입니다..."):
                        results = []
                        # 키워드 데이터 구조 호환성 처리
                        rk_list = [k['name'] if isinstance(k, dict) else k for k in rank_keywords]
                        for kw in rk_list:
                            rank_data = fetch_naver_rank(kw, target_name)
                            # collector_utils의 fetch_naver_rank 결과를 기반으로 노출 여부 판별
                            is_found = 1 <= rank_data.get('rank', 999) <= 100
                            
                            title = rank_data.get('title', '-')
                            link = rank_data.get('link', '-')
                            if link != "-":
                                title_html = f'<a href="{link}" target="_blank" style="text-decoration:none; color:#0366d6; font-weight:bold;">{title}</a>'
                            else:
                                title_html = title
        
                            results.append({
                                "키워드": kw,
                                "검색대상": target_name,
                                "노출 여부": is_found,
                                "순위/위치": rank_data['rank'] if is_found else 999,
                                "블로그명": rank_data.get('blogger', '-'),
                                "제목": title_html
                            })

                df = pd.DataFrame(results)
                
                # HTML 테이블 생성을 위한 커스텀 포맷터
                def format_status(val):
                    if val: return '<span class="badge badge-green">✅ 노출 중</span>'
                    return '<span class="badge badge-red">❌ 미노출</span>'
                
                def format_rank(val):
                    if val == 999: return '<span style="color: #8B95A1;">-</span>'
                    if val <= 5: color = "badge-green"
                    elif val <= 15: color = "badge-yellow"
                    else: color = "badge-red"
                    return f'<span class="badge {color}">{val}위</span>'

                df['노출 여부'] = df['노출 여부'].apply(format_status)
                df['순위/위치'] = df['순위/위치'].apply(format_rank)

                html_content = render_sortable_html_table(df)
                calc_height = len(df) * 48 + 50
                st.components.v1.html(html_content, height=calc_height, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    elif selected_menu == "키워드 선점 추천":
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("💡 LED 전광판 특화 키워드 선점 전략")
        st.markdown("""
        이 메뉴는 AI가 **LED 전광판** 시장의 흐름을 분석하여, 현재 우리가 네이버 블로그에서 선점하면 좋은 알짜배기 키워드들을 제안해 드립니다.
        """)
        
        col_m, col_b = st.columns([0.4, 0.6])
        ai_m = col_m.radio("분석 AI 모델", ["Gemini (1.5 Flash)", "GPT (4o)"], key="kw_ai_model", horizontal=True)
        
        if col_b.button("✨ LED 특화 키워드 발굴 시작", type="primary", use_container_width=True):
            m_type = 'gemini' if "Gemini" in ai_m else 'gpt'
            target_key = st.session_state['gemini_key'] if m_type == 'gemini' else st.session_state['openai_key']
            
            if not target_key:
                st.error(f"키워드 발굴을 위해 {m_type.upper()} API Key가 필요합니다. 설정 메뉴에서 입력해주세요.")
            else:
                with st.spinner(f"{ai_m}가 최신 LED 시장 트렌드를 분석 중입니다..."):
                    suggestions = ai_utils.generate_led_keywords(target_key, model_type=m_type)
                    st.markdown(suggestions)
                    st.download_button("💡 키워드 제안서 다운로드", data=suggestions, file_name=f"led_keyword_strategy_{m_type}.md")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
