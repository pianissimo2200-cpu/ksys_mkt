import time
import os
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import collector_utils as utils

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

# 유틸리티 함수 래핑
load_competitors = utils.load_competitors
save_competitors = utils.save_competitors
load_keywords = utils.load_keywords
save_keywords = utils.save_keywords
load_rank_keywords = utils.load_rank_keywords
save_rank_keywords = utils.save_rank_keywords
load_trend_keywords = utils.load_trend_keywords
save_trend_keywords = utils.save_trend_keywords
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

def main():
    st.set_page_config(page_title="마케팅 인사이트 대시보드", page_icon="📈", layout="wide")
    
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
    
    menu_options = ["📰 네이버 주요 뉴스 스크랩 통합", "🏢 경쟁사 최신 포스팅 스크랩 통합", "🏆 네이버 상위노출 현황", "📊 키워드 검색 트렌드 분석"]
    selected_menu = st.radio("메뉴 선택", menu_options, horizontal=True, label_visibility="collapsed")
    
    # --- 사이드바 영역 ---
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 1. 수집 기간 설정
        st.markdown("##### 📅 데이터 수집 기간")
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        date_range = st.date_input("조회 기간", value=(one_week_ago, today), max_value=today)
        if len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]
        else:
            st.stop()

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

        # 4. 경쟁사 관리
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
                st.dataframe(pd.concat(all_news), use_container_width=True, hide_index=True)

    elif selected_menu == "🏢 경쟁사 최신 포스팅 스크랩 통합":
        import ai_utils
        st.subheader("🏢 경쟁사 최신 포스팅 분석 및 AI 콘텐츠 어시스턴트")
        
        # 상단 설정 영역
        with st.expander("⚙️ AI 생성 설정 (API 키 및 자사 정보)", expanded=True):
            st.markdown("블로그 본문을 분석하고 AI가 글과 이미지를 자동 생성하기 위해 설정이 필요합니다.")
            
            c1, c2 = st.columns([0.8, 0.2])
            gemini_key = c1.text_input("Gemini API Key (텍스트 분석 및 생성용)", type="password")
            if c2.button("Gemini 키 확인", use_container_width=True):
                is_valid, msg = ai_utils.validate_gemini_key(gemini_key)
                if is_valid:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            
            c3, c4 = st.columns([0.8, 0.2])
            openai_key = c3.text_input("OpenAI API Key (DALL-E 3 이미지 생성용)", type="password")
            if c4.button("OpenAI 키 확인", use_container_width=True):
                is_valid, msg = ai_utils.validate_openai_key(openai_key)
                if is_valid:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
                    
            company_positioning = st.text_area("자사 기본 정보 및 강조할 강점", "예: 우리는 10년 경력의 설치 노하우가 있고, 가격 경쟁력이 뛰어나며 24시간 AS를 지원합니다.",             st.markdown("### 🤖 분석 및 콘텐츠 자동 생성")
            
            col_sel, col_opt, col_btn = st.columns([0.3, 0.4, 0.3])
            
            # 분석할 포스팅 선택
            titles = [f"[{b['업체명']}] {b['제목']}" for b in blogs]
            selected_title = col_sel.selectbox("분석할 포스팅 선택", titles)
            selected_post = blogs[titles.index(selected_title)]
            
            # 생성 모델 및 옵션
            with col_opt:
                ai_model = st.radio("사용할 AI 모델", ["Gemini (1.5 Flash)", "GPT (4o)"], horizontal=True)
                gen_option = st.radio("생성 범위", ["글만 생성", "이미지만 생성", "글 + 이미지 모두 생성"], horizontal=True)
            
            if col_btn.button("✨ 콘텐츠 생성 시작", use_container_width=True):
                # 모델 타입 결정
                m_type = 'gemini' if "Gemini" in ai_model else 'gpt'
                target_key = gemini_key if m_type == 'gemini' else openai_key
                
                if not target_key and ("글" in gen_option or "모두" in gen_option):
                    st.error(f"텍스트 생성을 위해 {m_type.upper()} API Key를 입력하고 [확인]을 눌러주세요.")
                elif not openai_key and ("이미지" in gen_option or "모두" in gen_option):
                    st.error("이미지 생성을 위해 OpenAI API Key를 입력하고 [확인]을 눌러주세요.")
                else:
                    with st.spinner("경쟁사 블로그 본문을 스크래핑하는 중..."):
                        full_content = utils.fetch_blog_full_content(selected_post['링크'])
                    
                    if not full_content:
                        st.error("본문 스크래핑에 실패했습니다. 네이버 블로그 구조가 아니거나 접근이 차단되었을 수 있습니다.")
                    else:
                        st.success(f"본문 추출 성공! {ai_model} 모델로 분석을 시작합니다.")
                        
                        col_l, col_r = st.columns(2)
                        
                        with col_l:
                            st.markdown("##### 📝 원본 내용 (수집된 본문)")
                            st.text_area("원본 본문", full_content[:1500] + "\n\n... (이하 생략)", height=300, disabled=True)
                        
                        with col_r:
                            st.markdown(f"##### 🤖 {ai_model} 생성 결과")
                            
                            topic_summary = selected_post['제목']
                            
                            # 텍스트 생성
                            if "글" in gen_option or "모두" in gen_option:
                                with st.spinner(f"{ai_model}가 분석 및 작성 중..."):
                                    generated_text = ai_utils.analyze_and_generate_post(full_content, company_positioning, target_key, model_type=m_type)
                                    st.markdown(generated_text)
                                    st.download_button("텍스트 다운로드", data=generated_text, file_name=f"generated_post_{m_type}.md", mime="text/markdown")
                                    topic_summary = generated_text[:200]
                            
                            # 이미지 생성
                            if "이미지" in gen_option or "모두" in gen_option:
                                with st.spinner("DALL-E 3가 썸네일 이미지를 생성하는 중..."):
                                    img_url, img_err = ai_utils.generate_blog_image(topic_summary, openai_key)
                                    if img_err:
                                        st.error(img_err)
                                    elif img_url:
                                        st.image(img_url, caption="생성된 AI 이미지", use_container_width=True)
                                        st.markdown(f"[이미지 원본 다운로드 링크]({img_url})")��성 결과")
                            
                            topic_summary = selected_post['제목']  # 이미지 프롬프트용 기본 요약
                            
                            # 텍스트 생성
                            if "글" in gen_option or "모두" in gen_option:
                                with st.spinner("AI가 본문을 분석하고 맞춤형 포스팅을 작성하는 중..."):
                                    generated_text = ai_utils.analyze_and_generate_post(full_content, company_positioning, gemini_key)
                                    st.markdown(generated_text)
                                    st.download_button("텍스트 다운로드", data=generated_text, file_name="generated_post.md", mime="text/markdown")
                                    # 요약 정보 추출 (이미지 생성을 위해)
                                    topic_summary = generated_text[:100] # 아주 간단한 처리
                            
                            # 이미지 생성
                            if "이미지" in gen_option or "모두" in gen_option:
                                with st.spinner("AI가 썸네일 이미지를 생성하는 중..."):
                                    img_url, img_err = ai_utils.generate_blog_image(topic_summary, openai_key)
                                    if img_err:
                                        st.error(img_err)
                                    elif img_url:
                                        st.image(img_url, caption="생성된 AI 이미지", use_container_width=True)
                                        st.markdown(f"[이미지 원본 다운로드 링크]({img_url})")

    elif selected_menu == "📊 키워드 검색 트렌드 분석":
        h_col1, h_col2 = st.columns([0.4, 0.6])
        h_col1.markdown("### 📈 검색량 트렌드")
        with h_col2:
            sc1, sc2, sc3 = st.columns([0.3, 0.4, 0.3])
            t_unit = sc1.selectbox("단위", ["date", "week", "month"], index=2, label_visibility="collapsed")
            d_range = sc2.date_input("기간", value=(datetime.date.today()-datetime.timedelta(days=365), datetime.date.today()), label_visibility="collapsed")
            sc3.markdown('<button style="width:100%; height:38px;">CSV 다운로드</button>', unsafe_allow_html=True)
        
        st.divider()
        if not trend_keywords:
            st.info("👈 좌측에서 트렌드 분석 키워드를 추가해 주세요.")
        else:
            show_absolute = st.toggle("절대 검색량(추정)으로 보기", value=True)
            if st.button("분석 실행", type="primary", use_container_width=True):
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
                    st.download_button("📊 CSV 다운로드", data=df_nv.to_csv(index=False).encode('utf-8'), file_name="trend.csv")

    elif selected_menu == "🏆 네이버 상위노출 현황":
        st.subheader("🏆 상위노출 현황")
        # 기존 로직 유지...
        pass

if __name__ == "__main__":
    main()
