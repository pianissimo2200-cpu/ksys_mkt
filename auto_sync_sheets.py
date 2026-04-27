import os
import datetime
import pandas as pd
import gspread
import requests
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import collector_utils as utils

# 1. 환경 변수 및 설정 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
COMPANY_NAME = os.environ.get("COMPANY_NAME", "자사")
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")
SA_API_KEY = os.environ.get("SA_API_KEY", "")
SA_SECRET_KEY = os.environ.get("SA_SECRET_KEY", "")
SA_CUSTOMER_ID = os.environ.get("SA_CUSTOMER_ID", "")
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
_creds_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "google-key.json")
if not os.path.isabs(_creds_file):
    CREDENTIALS_FILE = os.path.join(BASE_DIR, _creds_file)
else:
    CREDENTIALS_FILE = _creds_file

import sys
import argparse

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def send_slack_briefing(summary_data):
    if not SLACK_WEBHOOK_URL:
        print("경고: SLACK_WEBHOOK_URL이 설정되지 않아 알림을 건너뜁니다.")
        return

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 기본 헤더 구성
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚀 {COMPANY_NAME} 마켓 모니터링 브리핑 ({today_str})",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"오늘의 데이터 동기화가 완료되었습니다. <{f'https://docs.google.com/spreadsheets/d/{SHEET_ID}'}|[구글 시트 바로가기]>"
            }
        },
        {"type": "divider"}
    ]

    # --- 1. 뉴스 섹션 ---
    news_list = summary_data.get('news', [])
    news_text = "*📰 주요 뉴스 (최신 5건)*\n"
    if news_list:
        for i, item in enumerate(news_list[:5]):
            # item: [발행일, 키워드, 언론사, 제목, URL, 비고]
            news_text += f"{i+1}. [{item[2]}] <{item[4]}|{item[3]}>\n"
    else:
        news_text += "_오늘 수집된 뉴스가 없습니다._"
    
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": news_text}})

    # --- 2. 블로그 섹션 ---
    blog_list = summary_data.get('blog', [])
    blog_text = "\n*✍️ 경쟁사 블로그 최신 동향 (5건)*\n"
    if blog_list:
        for i, item in enumerate(blog_list[:5]):
            # item: [발행일, 업체명, 제목, URL, 비고]
            blog_text += f"{i+1}. *{item[1]}*: <{item[3]}|{item[2]}>\n"
    else:
        blog_text += "_오늘 수집된 블로그 포스팅이 없습니다._"
    
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": blog_text}})

    # --- 3.상위노출 섹션 (금요일 전용) ---
    rank_list = summary_data.get('rank', [])
    if rank_list:
        rank_text = "\n*📊 키워드 상위노출 현황 요약*\n"
        # 상위 5개 키워드만 예시로 노출
        for item in rank_list[:5]:
            # item: [날짜, 키워드, 전체검색량, PC, MO, 노출순위, 블로그명, 제목, URL, 비고]
            rank_text += f"• *{item[1]}*: {item[5]}위 ({item[6]})\n"
        blocks.append({"type": "divider"})
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": rank_text}})

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "💡 이 리포트는 매일 오전 9시에 자동으로 생성됩니다."
            }
        ]
    })

    payload = {"blocks": blocks}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("슬랙 브리핑 발송 완료!")
    except Exception as e:
        print(f"슬랙 발송 오류: {e}")

def sync_to_google_sheets(force_rank=False):
    print(f"[{datetime.datetime.now()}] 데이터 수집 및 구글 시트 동기화 시작...")
    
    # 수집된 데이터를 담을 요약 객체
    summary_data = {'news': [], 'blog': [], 'rank': []}
    
    if not SHEET_ID:
        print("에러: .env 파일에 GOOGLE_SHEET_ID가 설정되지 않았습니다.")
        return

    try:
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
    except Exception as e:
        print(f"에러: 구글 시트 연결 실패. {e}")
        return

    # 수집 대상 로드
    keywords = utils.load_keywords()
    competitors = utils.load_competitors()
    rank_keywords = utils.load_rank_keywords()
    trend_keywords = utils.load_trend_keywords()
    
    # 정기 수집 기간 설정 (어제 하루 데이터)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # --- 1. 뉴스 데이터 수집 및 업로드 (매일 실행) ---
    print(f"뉴스 수집 중... (대상: {len(keywords)}개 키워드)")
    news_sheet = spreadsheet.worksheet("뉴스클리핑")
    # 기존 데이터 로드 (중복 체크용: 날짜(0), 제목(3), URL(4))
    existing_news = news_sheet.get_all_values()
    seen_news = {f"{row[4]}|{row[0]}|{row[3]}" for row in existing_news if len(row) > 4}
    
    all_news_rows = []
    new_news_count = 0
    for kw in keywords:
        df = utils.fetch_naver_news(kw, yesterday, today, CLIENT_ID, CLIENT_SECRET)
        if not df.empty:
            for _, row in df.iterrows():
                # 중복 체크 키 생성
                key = f"{row['링크']}|{row['발행일']}|{row['제목']}"
                if key not in seen_news:
                    # 날짜｜키워드｜언론사｜제목｜URL｜비고
                    all_news_rows.append([row['발행일'], kw, row['언론사'], row['제목'], row['링크'], ""])
                    seen_news.add(key)
                    new_news_count += 1
    if all_news_rows:
        all_news_rows.sort(key=lambda x: x[0], reverse=True)
        news_sheet.append_rows(all_news_rows)
        summary_data['news'] = all_news_rows
        print(f" - 총 {len(all_news_rows)}건의 뉴스 기사 추가 완료 (신규건만 반영)")

    # --- 2. 경쟁사 블로그 수집 및 업로드 (매일 실행) ---
    print(f"경쟁사 블로그 수집 중... (대상: {len(competitors)}개 업체)")
    blog_sheet = spreadsheet.worksheet("블로그")
    # 기존 데이터 로드 (중복 체크용: 날짜(0), 제목(2), URL(3))
    existing_blogs = blog_sheet.get_all_values()
    seen_blogs = {f"{row[3]}|{row[0]}|{row[2]}" for row in existing_blogs if len(row) > 3}
    
    all_blog_rows = []
    new_blog_count = 0
    for comp in competitors:
        posts = utils.fetch_blog_feed(comp['url'], yesterday, today)
        if posts:
            for p in posts:
                key = f"{p['링크']}|{p['발행일']}|{p['제목']}"
                if key not in seen_blogs:
                    # 날짜｜업체명｜제목｜URL｜비고
                    all_blog_rows.append([p['발행일'], comp['name'], p['제목'], p['링크'], ""])
                    seen_blogs.add(key)
                    new_blog_count += 1
    if all_blog_rows:
        all_blog_rows.sort(key=lambda x: x[0], reverse=True)
        blog_sheet.append_rows(all_blog_rows)
        summary_data['blog'] = all_blog_rows
        print(f" - 총 {len(all_blog_rows)}건의 블로그 포스팅 추가 완료 (신규건만 반영)")

    # --- 3. 상위노출 및 검색량 수집 (금요일만 실행 또는 강제 실행 시) ---
    is_friday = (today.weekday() == 4)  # 4는 금요일
    if is_friday or force_rank:
        print(f"상위노출 현황 수집 중... (금요일 정기 수집)")
        rank_sheet = spreadsheet.worksheet("상위노출")
        # 기존 데이터 로드 (중복 체크용: 날짜(0), 키워드(1))
        existing_ranks = rank_sheet.get_all_values()
        seen_ranks = {f"{row[0]}|{row[1]}" for row in existing_ranks if len(row) > 1}
        
        rank_rows = []
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        for rk in rank_keywords:
            key = f"{today_str}|{rk}"
            if key not in seen_ranks:
                rank_res = utils.fetch_naver_rank(rk, CLIENT_ID, CLIENT_SECRET, search_target=COMPANY_NAME)
                vol_res = utils.fetch_naver_search_volume(rk, SA_API_KEY, SA_SECRET_KEY, SA_CUSTOMER_ID)
                # 날짜｜키워드｜전체검색량｜PC｜MO｜노출순위｜블로그명｜제목｜URL｜비고
                rank_rows.append([
                    today_str, rk, vol_res['total'], vol_res['pc'], vol_res['mobile'],
                    rank_res['rank'], rank_res['blogger'], rank_res['title'], rank_res['link'], ""
                ])
                seen_ranks.add(key)
        if rank_rows:
            rank_sheet.append_rows(rank_rows)
            summary_data['rank'] = rank_rows
            print(f" - 상위노출 현황 {len(rank_rows)}건 업데이트 완료")
    else:
        print("오늘은 금요일이 아니므로 상위노출 수집을 건너뜁니다. (매주 금요일 자동 실행)")

    # --- 4. 키워드 검색 트렌드 수집 및 업로드 (매월 1회 또는 강제 실행 시) ---
    is_first_day = (today.day == 1)
    if is_first_day or force_rank: # force_rank를 트렌드 강제 수집용으로도 사용
        print(f"키워드 검색 트렌드 수집 중...")
        try:
            # 트렌드 시트 확인 및 생성
            try:
                trend_sheet = spreadsheet.worksheet("키워드동향")
            except:
                trend_sheet = spreadsheet.add_worksheet(title="키워드동향", rows="1000", cols="10")
                trend_sheet.append_row(["날짜", "키워드", "트렌드지수", "수집일시"])
            
            # 검색 기간 설정 (최근 1년)
            start_date_str = (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
            end_date_str = today.strftime("%Y-%m-%d")
            
            trend_df = utils.fetch_naver_datalab_trend(trend_keywords, start_date_str, end_date_str, CLIENT_ID, CLIENT_SECRET)
            if not trend_df.empty:
                # 기존 데이터와 중복되지 않게 (날짜|키워드 기준) 처리하거나, 시트를 초기화하고 전체 다시 쓰기 (트렌드는 전체를 보는게 좋음)
                # 여기서는 간단히 전체 데이터를 덮어쓰거나 추가하는 방식 중 선택. 
                # 트렌드 지수는 상대값이므로 매번 전체를 가져와서 덮어쓰는 것이 정확합니다.
                trend_sheet.clear()
                trend_sheet.append_row(["날짜", "키워드", "트렌드지수", "수집일시"])
                
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                trend_rows = []
                for _, row in trend_df.iterrows():
                    trend_rows.append([row['날짜'], row['키워드'], row['트렌드지수'], now_str])
                
                if trend_rows:
                    trend_sheet.append_rows(trend_rows)
                    print(f" - {len(trend_rows)}건의 트렌드 지수 업데이트 완료")
        except Exception as e:
            print(f"트렌드 수집 중 오류 발생: {e}")

    # --- 5. 슬랙 브리핑 발송 ---
    send_slack_briefing(summary_data)

    print(f"[{datetime.datetime.now()}] 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-rank", action="store_true", help="금요일이 아니어도 상위노출 데이터를 수집합니다.")
    args = parser.parse_args()
    
    sync_to_google_sheets(force_rank=args.force_rank)
