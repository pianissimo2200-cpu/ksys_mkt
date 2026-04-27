import pandas as pd
import requests
import os
import datetime
import html
import json
import feedparser
import re
from urllib.parse import urlparse
import hashlib
import hmac
import base64
import time

# 기준 디렉토리 설정 (스크립트 위치 기반)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 환경 변수 로드용 (개별 실행 시)
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

COMPANY_NAME = os.environ.get("COMPANY_NAME", "자사")

COMPETITORS_FILE = os.path.join(BASE_DIR, "competitors.json")
KEYWORDS_FILE = os.path.join(BASE_DIR, "keywords.json")
RANK_KEYWORDS_FILE = os.path.join(BASE_DIR, "rank_keywords.json")

MEDIA_MAP = {
    "yna.co.kr": "연합뉴스",
    "news.naver.com": "네이버뉴스",
    "chosun.com": "조선일보",
    "donga.com": "동아일보",
    "hani.co.kr": "한겨레",
    "khan.co.kr": "경향신문",
    "sedaily.com": "서울경제",
    "hankyung.com": "한국경제",
    "mk.co.kr": "매일경제",
    "mt.co.kr": "머니투데이",
    "edaily.co.kr": "이데일리",
    "news1.kr": "뉴스1",
    "newsis.com": "뉴시스",
    "daily.hankooki.com": "데일리한국",
    "hankookilbo.com": "한국일보",
    "segye.com": "세계일보",
    "kmib.co.kr": "국민일보",
    "munhwa.com": "문화일보",
    "busan.com": "부산일보",
    "imaeil.com": "매일신문",
    "kukinews.com": "쿠키뉴스",
    "nocutnews.co.kr": "노컷뉴스",
    "ohmynews.com": "오마이뉴스",
    "pressian.com": "프레시안",
    "mediatoday.co.kr": "미디어오늘",
    "sisain.co.kr": "시사IN",
    "vop.co.kr": "민중의소리",
    "dailian.co.kr": "데일리안",
    "viewsnnews.com": "뷰스앤뉴스",
    "newdaily.co.kr": "뉴데일리",
    "sbs.co.kr": "SBS",
    "kbs.co.kr": "KBS",
    "mbc.co.kr": "MBC",
    "ytn.co.kr": "YTN",
    "news.tvchosun.com": "TV조선",
    "channela.com": "채널A",
    "jtbc.co.kr": "JTBC",
    "mbn.co.kr": "MBN",
    "ebs.co.kr": "EBS",
    "zdnet.co.kr": "ZDNet Korea",
    "bloter.net": "블로터",
    "inews24.com": "아이뉴스24",
    "digitaltoday.co.kr": "디지털투데이",
    "dt.co.kr": "디지털타임스",
    "etnews.com": "전자신문",
    "etnews.com": "전자신문",
    "koit.co.kr": "정보통신신문",
    "ksilbo.co.kr": "경상일보",
    "kwnews.co.kr": "강원일보",
    "kyeonggi.com": "경기일보",
    "kyeongin.com": "경인일보",
    "kyongbuk.co.kr": "경북일보",
    "ngetnews.com": "뉴스저널리즘",
    "newsjisang.com": "뉴스지상",
    "efnews.co.kr": "파이낸셜신문",
    "hq-times.com": "HQ타임스",
    "shinailbo.co.kr": "신아일보",
    "dizzotv.com": "디지틀조선TV",
    "geconomy.co.kr": "지이코노미",
    "cnbizm.com": "CNB뉴스",
    "m-i.kr": "매일일보",
    "ccnnews.co.kr": "충청뉴스",
    "ccdn.co.kr": "충청일보",
    "newspim.com": "뉴스핌",
    "asiae.co.kr": "아시아경제",
    "kbsm.net": "경북신문",
    "hidomin.com": "경북도민일보",
    "metroseoul.co.kr": "메트로신문",
    "dnews.co.kr": "대한경제",
    "joseilbo.com": "조세일보",
    "newsis.com": "뉴시스",
    "news1.kr": "뉴스1",
    "mt.co.kr": "머니투데이",
    "seoul.co.kr": "서울신문",
    "mhnse.com": "MHN스포츠",
    "sportschosun.com": "스포츠조선",
    "sports.donga.com": "스포츠동아",
    "starnewskorea.com": "스타뉴스",
    "gukjenews.com": "국제뉴스",
    "etoday.co.kr": "이투데이",
    "ajunews.com": "아주경제",
    "heraldcorp.com": "헤럴드경제",
    "kmib.co.kr": "국민일보",
    "dt.co.kr": "디지털타임스",
    "digitaltoday.co.kr": "디지털투데이",
    "zdnet.co.kr": "ZDNet Korea",
    "wowtv.co.kr": "한국경제TV",
    "bizwnews.com": "비즈월드",
    "lawissue.co.kr": "로이슈",
    "beyondpost.co.kr": "비욘드포스트",
    "pointp.co.kr": "포인트데일리",
}

def get_media_name(domain):
    domain = domain.replace("www.", "")
    if domain in MEDIA_MAP:
        return MEDIA_MAP[domain]
    for key, val in MEDIA_MAP.items():
        if key in domain:
            return val
    return domain

def load_competitors():
    if os.path.exists(COMPETITORS_FILE):
        with open(COMPETITORS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_competitors(data):
    with open(COMPETITORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return ["LED 전광판"]
    return ["LED 전광판"]

def save_keywords(data):
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_rank_keywords():
    if os.path.exists(RANK_KEYWORDS_FILE):
        with open(RANK_KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return [COMPANY_NAME, "LED전광판", "실내LED전광판", "학교LED전광판"]
    return [COMPANY_NAME, "LED전광판", "실내LED전광판", "학교LED전광판"]

def save_rank_keywords(data):
    with open(RANK_KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_naver_blog_id(url):
    match = re.search(r'blog\.naver\.com/([^/?]+)', url)
    if match:
        return match.group(1)
    match = re.search(r'm\.blog\.naver\.com/([^/?]+)', url)
    if match:
        return match.group(1)
    return None

def fetch_blog_feed(url, start_date, end_date):
    nid = extract_naver_blog_id(url)
    if nid:
        rss_url = f"https://rss.blog.naver.com/{nid}.xml"
    else:
        rss_url = url + ("rss" if url.endswith('/') else "/rss")

    feed = feedparser.parse(rss_url)
    posts = []
    if not feed.entries:
        return posts
        
    for entry in feed.entries:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime.datetime(*entry.published_parsed[:6])
            if start_date <= pub_date.date() <= end_date:
                posts.append({
                    "제목": html.unescape(entry.title),
                    "링크": entry.link,
                    "발행일": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "요약": html.unescape(entry.get('description', '')[:100] + '...')
                })
    return posts

def fetch_naver_news(query, start_date, end_date, client_id, client_secret):
    if not client_id or not client_secret:
        return pd.DataFrame()

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    all_items = []
    for start in range(1, 1000, 100):
        params = {"query": query, "display": 100, "start": start, "sort": "date"}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items: break
                
            for item in items:
                try:
                    pub_date = datetime.datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S %z")
                    pub_date_local = pub_date.date()
                    if start_date <= pub_date_local <= end_date:
                        clean_title = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
                        original_link = item.get('originallink', item.get('link', ''))
                        domain = urlparse(original_link).netloc if original_link else "알 수 없음"
                        media_name = get_media_name(domain)
                        all_items.append({
                            "제목": clean_title, "링크": item['link'], "언론사": media_name, "발행일": pub_date.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    elif pub_date_local < start_date:
                        return pd.DataFrame(all_items)
                except: continue
            if len(items) < 100: break
        except: break
    return pd.DataFrame(all_items)

def fetch_naver_rank(query, client_id, client_secret, search_target=None):
    if search_target is None:
        search_target = COMPANY_NAME
    if not client_id or not client_secret:
        return {"rank": -1, "title": "인증 정보 없음", "desc": "-", "link": "-"}

    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": query, "display": 100, "start": 1, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        
        for idx, item in enumerate(items):
            title = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
            desc = html.unescape(item['description'].replace('<b>', '').replace('</b>', ''))
            blogger = html.unescape(item.get('bloggername', ''))
            if search_target in title or search_target in desc or search_target in blogger:
                return {
                    "rank": idx + 1, "blogger": blogger, "title": title,
                    "desc": desc[:100] + "..." if len(desc) > 100 else desc, "link": item.get('link', '')
                }
        return {"rank": 999, "blogger": "-", "title": f"100위권 내 {search_target} 노출 없음", "desc": "-", "link": "-"}
    except Exception as e:
        return {"rank": -1, "blogger": "-", "title": f"에러: {e}", "desc": "-", "link": "-"}

def generate_signature(timestamp, method, path, secret_key):
    message = f"{timestamp}.{method}.{path}".encode("utf-8")
    signing_key = secret_key.encode("utf-8")
    hash_value = hmac.new(signing_key, message, hashlib.sha256).digest()
    return base64.b64encode(hash_value).decode()

def fetch_naver_search_volume(keyword, api_key, secret_key, customer_id):
    if not api_key or not secret_key or not customer_id:
        return {"pc": 0, "mobile": 0, "total": 0}
        
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/keywordstool"
    signature = generate_signature(timestamp, method, path, secret_key)
    
    headers = {"X-Timestamp": timestamp, "X-API-KEY": api_key, "X-Customer": customer_id, "X-Signature": signature}
    url = f"https://api.naver.com{path}?hintKeywords={keyword}&showDetail=1"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        keyword_no_space = keyword.replace(" ", "")
        for item in data.get("keywordList", []):
            if item.get("relKeyword", "").replace(" ", "") == keyword_no_space:
                pc = item.get("monthlyPcQcCnt", 0)
                mobile = item.get("monthlyMobileQcCnt", 0)
                if isinstance(pc, str): pc = 10 if "<" in pc else int(pc)
                if isinstance(mobile, str): mobile = 10 if "<" in mobile else int(mobile)
                return {"pc": pc, "mobile": mobile, "total": pc + mobile}
        return {"pc": 0, "mobile": 0, "total": 0}
    except:
        return {"pc": 0, "mobile": 0, "total": 0}

def fetch_naver_datalab_trend(keywords, start_date, end_date, client_id, client_secret, time_unit='month'):
    if not client_id or not client_secret:
        return pd.DataFrame()

    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

    # 키워드 그룹 구성 (단일 키워드별 그룹화)
    keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords]

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for group in data.get('results', []):
            group_name = group['title']
            for entry in group.get('data', []):
                results.append({
                    "날짜": entry['period'],
                    "키워드": group_name,
                    "트렌드지수": entry['ratio']
                })
        
        if not results:
            return pd.DataFrame()
            
        df = pd.DataFrame(results)
        return df
    except Exception as e:
        print(f"데이터랩 API 오류: {e}")
        return pd.DataFrame()
