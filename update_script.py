import os

file_path = r"c:\01.Project\app.py"
with open(file_path, "r", encoding="utf-8") as f:
    orig = f.read()

# Find everything up to "def main():"
idx = orig.find("def main():")
if idx == -1:
    print("Error: Could not find main()")
    exit(1)

head = orig[:idx]

new_main = """def main():
    st.set_page_config(page_title="마케팅 인사이트 대시보드", page_icon="📈", layout="wide")
    
    st.title("📈 마케팅 인사이트 대시보드")
    st.markdown("네이버 Search API를 활용한 뉴스 수집 및 경쟁사 블로그 모니터링 시스템입니다.")
    
    competitors = load_competitors()
    keywords = load_keywords()
    rank_keywords = load_rank_keywords()
    
    # 📌 상단 메뉴 렌더링 (기존 탭 대체)
    menu_options = ["📰 네이버 주요 뉴스 스크랩 통합", "🏢 경쟁사 최신 포스팅 스크랩 통합", "🏆 네이버 상위노출 현황"]
    selected_menu = st.radio("메뉴 선택", menu_options, horizontal=True, label_visibility="collapsed")
    
    # --- 사이드바 영역 ---
    with st.sidebar:
        # 사이드바 전체 리스트 요소를 위한 공통 CSS 주입
        st.markdown(\"\"\"
        <style>
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: 0px !important;
            margin-bottom: -12px;
        }
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
            opacity: 0;
            transition: opacity 0.2s ease;
            padding: 0px !important;
            margin: 0px !important;
            border: none !important;
            background: transparent !important;
            color: #ff4b4b !important;
            min-height: 25px !important;
            font-weight: bold;
            display: flex;
            justify-content: flex-end;
        }
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover button {
            opacity: 1;
        }
        </style>
        \"\"\", unsafe_allow_html=True)
        
        st.header("⚙️ 주요 설정 (데이터 수집 기간)")
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        with st.form("date_setting_form"):
            start_date = st.date_input("시작일", value=one_week_ago)
            end_date = st.date_input("종료일", value=today)
            apply_date_btn = st.form_submit_button("기간 설정 완료")
        if start_date > end_date:
            st.error("⚠️ 시작일이 종료일보다 이후일 수 없습니다.")
            st.stop()
        st.info("💡 **Tips**\\n\\n기간을 길게 설정할수록 대상 데이터 수집에 다소 시간이 걸릴 수 있습니다.")
        
        def render_news_manager(expanded):
            st.divider()
            st.header("🔑 뉴스 수집 키워드 관리")
            with st.expander("➕ 관심 키워드 추가", expanded=expanded):
                with st.form("add_keyword_sidebar", clear_on_submit=True):
                    new_kw = st.text_input("새로운 키워드 창", placeholder="예: 옥외광고, 스마트 사이니지")
                    submitted_kw = st.form_submit_button("목록에 추가")
                    if submitted_kw:
                        if new_kw.strip():
                            if new_kw.strip() in keywords:
                                st.warning("이미 등록된 키워드입니다.")
                            else:
                                keywords.append(new_kw.strip())
                                save_keywords(keywords)
                                st.success(f"'{new_kw}' (이)가 추가되었습니다!")
                                st.rerun()
                        else:
                            st.error("키워드를 입력해주세요.")
            if keywords:
                st.markdown("##### 📌 모니터링 키워드 목록")
                for i, kw in enumerate(keywords):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"<span style='font-size:14px; font-weight:500;'>{kw}</span>", unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"del_kw_{i}"):
                            keywords.pop(i)
                            save_keywords(keywords)
                            st.rerun()

        def render_competitor_manager(expanded):
            st.divider()
            st.header("🏢 경쟁사 블로그 관리")
            with st.expander("➕ 경쟁사 블로그 스크랩 등록", expanded=expanded):
                with st.form("add_competitor_sidebar", clear_on_submit=True):
                    new_name = st.text_input("업체명", placeholder="예: 삼성전자")
                    new_url = st.text_input("블로그 주소", placeholder="예: https://blog.naver.com/sec")
                    submitted_comp = st.form_submit_button("목록에 추가")
                    if submitted_comp:
                        if new_name.strip() and new_url.strip():
                            if any(c['url'] == new_url.strip() for c in competitors):
                                st.warning("이미 등록된 블로그입니다.")
                            else:
                                competitors.append({"name": new_name.strip(), "url": new_url.strip()})
                                save_competitors(competitors)
                                st.success(f"'{new_name}' 등록 성공!")
                                st.rerun()
                        else:
                            st.error("업체명과 주소를 꽉 채워주세요.")
            if competitors:
                st.markdown("##### 📌 모니터링 대상 업체 목록")
                for i, comp in enumerate(competitors):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"<span style='font-size:14px; font-weight:500;'>{comp['name']}</span>", unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"del_sidebar_{i}"):
                            competitors.pop(i)
                            save_competitors(competitors)
                            st.rerun()

        def render_rank_manager(expanded):
            st.divider()
            st.header("🏆 상위노출 키워드 관리")
            with st.expander("➕ 상위노출 모니터링 키워드 추가", expanded=expanded):
                with st.form("add_rank_keyword_sidebar", clear_on_submit=True):
                    new_rk = st.text_input("확인할 네이버 검색어", placeholder="예: 부산LED전광판")
                    submitted_rk = st.form_submit_button("키워드 목록에 추가")
                    if submitted_rk:
                        if new_rk.strip():
                            if new_rk.strip() in rank_keywords:
                                st.warning("이미 등록된 키워드입니다.")
                            else:
                                rank_keywords.append(new_rk.strip())
                                save_rank_keywords(rank_keywords)
                                st.success(f"'{new_rk}' (이)가 상위노출 목록에 추가되었습니다!")
                                st.rerun()
                        else:
                            st.error("키워드를 입력해주세요.")
            if rank_keywords:
                st.markdown("##### 📌 상위노출 확인 대상 목록")
                for i, rk in enumerate(rank_keywords):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"<span style='font-size:14px; font-weight:500;'>{rk}</span>", unsafe_allow_html=True)
                    with col2:
                        if st.button("✖", key=f"del_rk_{i}"):
                            rank_keywords.pop(i)
                            save_rank_keywords(rank_keywords)
                            st.rerun()

        if selected_menu == "📰 네이버 주요 뉴스 스크랩 통합":
            render_news_manager(expanded=True)
            render_competitor_manager(expanded=False)
            render_rank_manager(expanded=False)
        elif selected_menu == "🏢 경쟁사 최신 포스팅 스크랩 통합":
            render_competitor_manager(expanded=True)
            render_news_manager(expanded=False)
            render_rank_manager(expanded=False)
        elif selected_menu == "🏆 네이버 상위노출 현황":
            render_rank_manager(expanded=True)
            render_news_manager(expanded=False)
            render_competitor_manager(expanded=False)

    # ===== TAB 1: 네이버 뉴스 스크랩 (다중 키워드) =====
    if selected_menu == "📰 네이버 주요 뉴스 스크랩 통합":
        st.subheader("📰 관심 키워드 관련 최신 뉴스 통합 브리핑")
        if not keywords:
            st.info("👈 좌측 사이드바의 '뉴스 수집 키워드 관리'에서 수집할 키워드를 먼저 1개 이상 추가해 주세요.")
        else:
            if st.button("등록된 키워드 뉴스 전체 수집 시작", type="primary", use_container_width=True):
                all_news_aggregated = []
                with st.spinner(f"네이버 뉴스에서 총 {len(keywords)}개의 키워드에 대한 기사를 스크랩 통합 중입니다. 잠시만 기다려주세요..."):
                    for kw in keywords:
                        df = fetch_naver_news(kw, start_date, end_date)
                        if not df.empty:
                            df.insert(0, '검색 키워드', kw)
                            all_news_aggregated.append(df)
                        else:
                            empty_df = pd.DataFrame([{
                                "검색 키워드": kw,
                                "제목": "해당 키워드로 검색된 최신 뉴스가 없습니다.",
                                "링크": "-",
                                "언론사": "-",
                                "발행일": "-"
                            }])
                            all_news_aggregated.append(empty_df)
                if all_news_aggregated:
                    df_all_news = pd.concat(all_news_aggregated, ignore_index=True)
                    df_all_news = df_all_news.sort_values(by="발행일", ascending=False).reset_index(drop=True)
                    st.success(f"성공적으로 총 {len(df_all_news)}건의 뉴스 기사를 수집했습니다!")
                    st.dataframe(
                        df_all_news,
                        column_config={
                            "검색 키워드": st.column_config.TextColumn("검색 키워드", width="small"),
                            "제목": st.column_config.TextColumn("기사 제목", width="large"),
                            "링크": st.column_config.LinkColumn("기사 링크 (이동)", width="small"),
                            "언론사": st.column_config.TextColumn("도메인/언론", width="small"),
                            "발행일": st.column_config.DatetimeColumn("발행 일시", format="YYYY-MM-DD HH:mm", width="medium"),
                        },
                        use_container_width=True,
                        hide_index=True,
                        height=600
                    )
                else:
                    st.warning("해당 기간 내 등록된 키워드들로 수집된 뉴스가 없거나 수집에 실패했습니다.")

    # ===== TAB 2: 경쟁사 블로그 대시보드 (통합형) =====
    elif selected_menu == "🏢 경쟁사 최신 포스팅 스크랩 통합":
        st.subheader("🏢 모든 경쟁사 최근 포스팅 통합 타임라인")
        if not competitors:
            st.info("👈 좌측 사이드바의 '경쟁사 블로그 관리'에서 모니터링할 업체를 먼저 추가해 주세요.")
        else:
            if st.button("경쟁사 블로그 통합 수집 시작", type="primary", use_container_width=True):
                all_posts_aggregated = []
                with st.spinner("모든 경쟁사 블로그에서 새로운 글을 스크랩하여 통합 중입니다..."):
                    for comp in competitors:
                        posts = fetch_blog_feed(comp['url'], start_date, end_date)
                        for p in posts:
                            all_posts_aggregated.append({
                                "업체명": comp['name'],
                                "발행일시": p["발행일"],
                                "글제목": p["제목"],
                                "내용요약": p["요약"],
                                "원문보기": p["링크"]
                            })
                if not all_posts_aggregated:
                    st.warning("등록된 경쟁사 블로그에서 수집 가능한 최신 포스팅이 하나도 없습니다.")
                else:
                    df_all = pd.DataFrame(all_posts_aggregated)
                    df_all = df_all.sort_values(by="발행일시", ascending=False).reset_index(drop=True)
                    st.markdown(f"**✔ 총 {len(df_all)}개의 포스팅 내역이 최신 날짜순으로 정렬되었습니다.**")
                    st.dataframe(
                        df_all,
                        column_config={
                            "업체명": st.column_config.TextColumn("업체명", width="small"),
                            "발행일시": st.column_config.TextColumn("발행일시", width="medium"),
                            "글제목": st.column_config.TextColumn("글제목", width="medium"),
                            "내용요약": st.column_config.TextColumn("내용요약", width="large"),
                            "원문보기": st.column_config.LinkColumn("원문보기 (클릭)", width="small"),
                        },
                        use_container_width=True,
                        hide_index=True,
                        height=600
                    )

    # ===== TAB 3: 네이버 상위노출 현황 =====
    elif selected_menu == "🏆 네이버 상위노출 현황":
        st.subheader("🏆 키워드별 '케이시스' 최상단 노출 현황")
        st.markdown(
            "네이버 블로그 검색(유사도순) 결과 상위 100위 내에 **'케이시스'**가 포함된 포스팅의 최고 순위를 점검합니다.\\n\\n"
            "💡 **순위별 색상 안내**: 🟢 **초록색** (1위-5위) / 🟠 **주황색** (6위-10위) / 🔴 **빨간색** (11위 밖 및 미노출)"
        )
        if not rank_keywords:
            st.info("👈 좌측 사이드바의 '상위노출 키워드 관리'에서 모니터링할 키워드를 추가해 주세요.")
        else:
            if st.button("전체 상위노출 현황 조회 시작", type="primary", use_container_width=True):
                rank_results = []
                with st.spinner("지정된 키워드별로 상위 노출 위치를 분석 중입니다..."):
                    for rk in rank_keywords:
                        result = fetch_naver_rank(rk, search_target="케이시스")
                        volume = fetch_naver_search_volume(rk)
                        rank_results.append({
                            "검색 키워드": rk,
                            "월간 검색(PC)": volume["pc"],
                            "월간 검색(MO)": volume["mobile"],
                            "월간 총검색량": volume["total"],
                            "최고 순위": result["rank"],
                            "블로그명": result.get("blogger", "-"),
                            "노출 제목": result["title"],
                            "미리보기 요약": result["desc"],
                            "바로가기 링크": result["link"]
                        })
                if rank_results:
                    df_rank = pd.DataFrame(rank_results)
                    def format_rank(val):
                        if val == 999: return "100위 밖 (노출 안됨)"
                        elif val == -1: return "API/검색 오류"
                        else: return f"{val}위"
                    df_rank['순위_raw'] = df_rank['최고 순위']
                    df_rank['최고 순위'] = df_rank['최고 순위'].apply(format_rank)
                    def highlight_rank(row):
                        rank_val = row['순위_raw']
                        if 1 <= rank_val <= 5: return ['background-color: #d4edda; color: #155724'] * len(row)
                        elif 6 <= rank_val <= 10: return ['background-color: #fff3cd; color: #856404'] * len(row)
                        elif rank_val == 999 or rank_val > 10: return ['background-color: #f8d7da; color: #721c24'] * len(row)
                        else: return [''] * len(row)
                    styled_df = df_rank.style.apply(highlight_rank, axis=1)
                    st.dataframe(
                        styled_df,
                        column_config={
                            "검색 키워드": st.column_config.TextColumn("검색 키워드", width="small", help="모니터링 대상으로 등록된 네이버 검색어입니다."),
                            "월간 검색(PC)": st.column_config.NumberColumn("PC 검색량", width="small", help="네이버 검색광고 기준 최근 한 달간(30일) PC 기기에서 해당 키워드가 검색된 횟수입니다."),
                            "월간 검색(MO)": st.column_config.NumberColumn("MO 검색량", width="small", help="네이버 검색광고 기준 최근 한 달간(30일) 모바일 기기에서 해당 키워드가 검색된 횟수입니다."),
                            "월간 총검색량": st.column_config.NumberColumn("총 검색량(월)", width="small", help="PC와 모바일을 합산한 최근 한 달간의 총 검색 횟수 지표입니다."),
                            "최고 순위": st.column_config.TextColumn("현재 노출 순위", width="small", help="네이버 블로그 검색 API (유사도순) 기준 상위 100위 내에서 '케이시스'가 언급된 포스팅이 위치한 가장 높은 노출 순위입니다."),
                            "블로그명": st.column_config.TextColumn("작성 블로그명", width="medium", help="해당 게시물을 발행한 작성자(블로그)의 공식 명칭입니다."),
                            "노출 제목": st.column_config.TextColumn("노출된 게시물 제목", width="medium", help="검색에 노출된 해당 포스팅의 실제 제목입니다."),
                            "미리보기 요약": st.column_config.TextColumn("포스팅 요약", width="large", help="검색 결과에서 확인되는 포스팅 내용의 일부 요약입니다."),
                            "바로가기 링크": st.column_config.LinkColumn("원문 이동", width="small", help="클릭 시 해당 블로그 포스팅 원문 페이지로 새 탭에서 이동합니다."),
                            "순위_raw": None
                        },
                        use_container_width=True,
                        hide_index=True
                    )

if __name__ == "__main__":
    main()
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(head + new_main)
print("Updated successfully")
