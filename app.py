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

# 환경 변수 로드 (.env)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
COMPANY_NAME = os.environ.get("COMPANY_NAME", "자사")

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
        # 로그인 화면 출력
        st.title("🔒 케이시스 마케팅 인사이트")
        st.text_input("접속 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 비밀번호가 틀렸습니다.")
        return False
    return True

def main():
    st.set_page_config(page_title="마케팅 인사이트 대시보드", page_icon="📈", layout="wide")
    
    # API 키 초기 로드 (함수 최상단에서 선언하여 에러 방지)
    st.session_state['gemini_key'] = os.environ.get("GEMINI_API_KEY", get_secret("GEMINI_API_KEY", ""))
    st.session_state['openai_key'] = os.environ.get("OPENAI_API_KEY", get_secret("OPENAI_API_KEY", ""))
    
    if not check_password():
        st.stop()  # 비밀번호가 틀리면 여기서 멈춤
    
    # 크롬 브라우저 자동번역 방지 스크립트
    st.components.v1.html(
        """<script>window.parent.document.documentElement.lang = 'ko';window.parent.document.body.setAttribute('translate', 'no');</script>""",
        height=0, width=0
    )
    
    st.title("📈 마케팅 인사이트 대시보드")
    
    competitors = load_competitors()
    keywords = load_keywords()
    rank_keywords = load_rank_keywords()
    trend_keywords = load_trend_keywords()
    
    menu_options = ["📰 네이버 주요 뉴스 스크랩 통합", "🏢 경쟁사 최신 포스팅 스크랩 통합", "🏆 네이버 상위노출 현황", "📊 키워드 검색 트렌드 분석", "💡 LED 특화 키워드 선점 추천"]
    selected_menu = st.radio("메뉴 선택", menu_options, horizontal=True, label_visibility="collapsed")
    
    # --- 사이드바 영역 ---
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 1. 수집 기간 설정
        st.markdown("##### 📅 데이터 수집 기간")
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        date_range = st.date_input("조회 기간", value=(one_week_ago, today), max_value=today)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]
        else:
            start_date, end_date = today, today

        # 2. 뉴스 키워드 관리
        with st.expander("🔑 뉴스 수집 키워드 관리", expanded=(selected_menu == "📰 네이버 주요 뉴스 스크랩 통합")):
            new_kw = st.text_input("뉴스 키워드 추가")
            if st.button("뉴스 키워드 저장"):
                if new_kw and new_kw not in keywords:
                    keywords.append(new_kw)
                    save_keywords(keywords)
                    st.rerun()
            for i, kw in enumerate(keywords):
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"• {kw}")
                if col2.button("X", key=f"del_nw_{i}"):
                    keywords.pop(i)
                    save_keywords(keywords)
                    st.rerun()

        # 3. 트렌드 키워드 관리
        with st.expander("📊 트렌드 분석 키워드 관리", expanded=(selected_menu == "📊 키워드 검색 트렌드 분석")):
            new_tk = st.text_input("트렌드 키워드 추가")
            if st.button("트렌드 키워드 저장"):
                if new_tk and new_tk not in trend_keywords:
                    trend_keywords.append(new_tk)
                    save_trend_keywords(trend_keywords)
                    st.rerun()
            for i, tk in enumerate(trend_keywords):
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"• {tk}")
                if col2.button("X", key=f"del_tk_{i}"):
                    trend_keywords.pop(i)
                    save_trend_keywords(trend_keywords)
                    st.rerun()

        # 4. 상위노출 키워드 관리
        with st.expander("🏆 상위노출 키워드 관리", expanded=(selected_menu == "🏆 네이버 상위노출 현황")):
            new_rk = st.text_input("상위노출 키워드 추가")
            if st.button("상위노출 키워드 저장"):
                if new_rk and new_rk not in rank_keywords:
                    rank_keywords.append(new_rk)
                    save_rank_keywords(rank_keywords)
                    st.rerun()
            for i, rk in enumerate(rank_keywords):
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"• {rk}")
                if col2.button("X", key=f"del_rk_{i}"):
                    rank_keywords.pop(i)
                    save_rank_keywords(rank_keywords)
                    st.rerun()

        # 5. 경쟁사 관리
        with st.expander("🏢 경쟁사 블로그 관리", expanded=(selected_menu == "🏢 경쟁사 최신 포스팅 스크랩 통합")):
            new_name = st.text_input("업체명")
            new_url = st.text_input("블로그URL")
            if st.button("경쟁사 등록"):
                if new_name and new_url:
                    competitors.append({"name": new_name, "url": new_url})
                    save_competitors(competitors)
                    st.rerun()
            for i, comp in enumerate(competitors):
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"• {comp['name']}")
                if col2.button("X", key=f"del_comp_{i}"):
                    competitors.pop(i)
                    save_competitors(competitors)
                    st.rerun()

        st.divider()
        # 구글 시트 연동 상태 표시
        if utils.check_gsheet_connection():
            st.success("✅ 구글 시트 연동 중")
            st.caption("데이터가 실시간으로 영구 저장됩니다.")
        else:
            st.error("❌ 구글 시트 연결 실패")
            st.caption("로컬 모드: 재접속 시 데이터 유실 위험")
            if st.button("새로고침/재시도"):
                st.rerun()

    # ===== 메뉴별 화면 렌더링 =====
    if selected_menu == "📰 네이버 주요 뉴스 스크랩 통합":
        st.subheader("📰 뉴스 통합 브리핑")
        if st.button("뉴스 수집 시작", type="primary", use_container_width=True):
            all_news = []
            for kw in keywords:
                df = fetch_naver_news(kw, start_date, end_date)
                if not df.empty:
                    df.insert(0, '키워드', kw)
                    all_news.append(df)
            if all_news:
                st.dataframe(
                    pd.concat(all_news), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "링크": st.column_config.LinkColumn("링크", display_text="🔗 링크 열기")
                    }
                )

    elif selected_menu == "🏢 경쟁사 최신 포스팅 스크랩 통합":
        st.subheader("🏢 경쟁사 최신 포스팅 분석 및 AI 콘텐츠 어시스턴트")
        
        with st.expander("⚙️ AI 생성 설정 (API 키 및 자사 정보)", expanded=False):
            st.markdown("블로그 본문을 분석하고 AI가 글과 이미지를 자동 생성하기 위해 설정이 필요합니다.")
            
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
                st.info("해당 기간 내 수집된 포스팅이 없습니다.")

        if 'latest_blogs' in st.session_state and st.session_state['latest_blogs']:
            blogs_df = pd.DataFrame(st.session_state['latest_blogs'])
            st.dataframe(
                blogs_df[['업체명', '발행일', '제목', '링크']], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "링크": st.column_config.LinkColumn("링크", display_text="🔗 포스팅 열기")
                }
            )
            
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
                            st.markdown("##### 📝 원본 내용 (요약)")
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

    elif selected_menu == "📊 키워드 검색 트렌드 분석":
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
                    df_nv = fetch_naver_datalab_trend(trend_keywords, d_range[0].strftime("%Y-%m-%d"), d_range[1].strftime("%Y-%m-%d"), time_unit=t_unit)
                    if not df_nv.empty:
                        if show_absolute:
                            for kw in trend_keywords:
                                vol = fetch_naver_search_volume(kw)
                                max_ratio = df_nv[df_nv['키워드'] == kw]['트렌드지수'].max()
                                scaler = vol['total'] / (max_ratio if max_ratio > 0 else 1)
                                df_nv.loc[df_nv['키워드'] == kw, '표시수치'] = df_nv['트렌드지수'] * scaler
                        else:
                            df_nv['표시수치'] = df_nv['트렌드지수']
                        
                        fig = px.line(df_nv, x='날짜', y='표시수치', color='키워드', markers=True, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                        st.download_button("📊 CSV 다운로드", data=df_nv.to_csv(index=False).encode('utf-8'), file_name="trend_analysis.csv")
                else:
                    st.warning("기간을 시작일과 종료일 모두 선택해주세요.")

    elif selected_menu == "🏆 네이버 상위노출 현황":
        st.subheader("🏆 네이버 통합검색 상위노출 현황")
        if not rank_keywords:
            st.info("👈 좌측 설정에서 상위노출을 확인할 키워드를 관리해주세요.")
        else:
            target_name = st.text_input("추적할 업체/브랜드명 (미입력 시 자사명)", value=COMPANY_NAME)
            if st.button("순위 추적 시작", type="primary", use_container_width=True):
                results = []
                for kw in rank_keywords:
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
                        "노출 여부": "✅ 노출 중" if is_found else "❌ 미노출",
                        "순위/위치": f"{rank_data['rank']}위 (블로그)" if is_found else "-",
                        "블로그명": rank_data.get('blogger', '-'),
                        "제목": title_html
                    })
                
                df = pd.DataFrame(results)
                
                def highlight_row(row):
                    val = row['순위/위치']
                    if val == "-": 
                        color = '#f8d7da' # 빨간색
                    else:
                        try:
                            rank = int(val.split("위")[0])
                            if rank <= 5: color = '#d4edda' # 초록색
                            elif 6 <= rank <= 15: color = '#fff3cd' # 노란색
                            else: color = '#f8d7da' # 빨간색
                        except:
                            color = '#f8d7da'
                    return [f'background-color: {color}; color: black'] * len(row)

                styled_df = df.style.apply(highlight_row, axis=1).hide(axis="index")
                
                table_html = styled_df.set_table_styles([
                    {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse'), ('margin-top', '10px'), ('font-size', '14px')]},
                    {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '12px 8px'), ('text-align', 'left')]},
                    {'selector': 'th', 'props': [('background-color', '#f8f9fa'), ('font-weight', 'bold'), ('color', '#333'), ('white-space', 'nowrap')]},
                    # 키워드, 검색대상, 노출여부, 순위/위치 컬럼은 줄바꿈 방지
                    {'selector': 'td:nth-child(1), td:nth-child(2), td:nth-child(3), td:nth-child(4)', 'props': [('white-space', 'nowrap'), ('min-width', '80px')]},
                    # 제목 컬럼은 최소 너비 확보 및 자연스러운 줄바꿈
                    {'selector': 'td:nth-child(6)', 'props': [('min-width', '300px')]}
                ]).to_html(escape=False)
                
                st.markdown(table_html, unsafe_allow_html=True)

    elif selected_menu == "💡 LED 특화 키워드 선점 추천":
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

if __name__ == "__main__":
    main()
