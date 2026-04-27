# 📈 마케팅 인사이트 모니터링 솔루션 설치 및 사용 가이드

본 프로그램은 네이버 API와 구글 스프레드시트를 연동하여 자동 뉴스클리핑, 경쟁사 블로그 모니터링, 키워드 트렌드 분석을 수행하는 통합 솔루션입니다.

## 📁 주요 파일 구성
- `app.py`: 웹 대시보드 실행 파일 (Streamlit 기반)
- `auto_sync_sheets.py`: 구글 시트 자동 동기화 및 슬랙 알림 발송 스크립트
- `collector_utils.py`: 데이터 수집 공통 유틸리티
- `.env.example`: 환경 변수 설정 템플릿 (파일명을 `.env`로 변경하여 사용)
- `*.json`: 키워드 및 경쟁사 관리용 데이터 파일

## ⚙️ 초기 세팅 방법

### 1. 필수 라이브러리 설치
Python 3.8 이상 환경에서 아래 명령어를 실행하여 필요한 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

### 2. API 키 발급 및 설정
`.env.example` 파일을 복사하여 `.env` 파일을 만들고 아래 정보를 입력합니다.

- **네이버 API**: [네이버 개발자 센터](https://developers.naver.com/main/)에서 '검색' 및 '데이터랩(검색어트렌드)' 권한이 있는 Client ID/Secret을 발급받습니다.
- **네이버 검색광고 API**: [네이버 검색광고 API 센터](https://searchad.naver.com/)에서 API 키를 발급받습니다 (검색량 조회용).
- **구글 서비스 계정**: [Google Cloud Console](https://console.cloud.google.com/)에서 서비스 계정을 생성하고 JSON 키 파일을 다운로드하여 `google-key.json`으로 이름을 변경해 폴더에 넣습니다.
- **슬랙 웹훅**: 알림을 받을 채널의 Incoming Webhook URL을 생성합니다.

### 3. 회사명 설정
`.env` 파일의 `COMPANY_NAME` 항목에 귀사의 이름을 입력하세요. 대시보드와 알림 메시지에 자동으로 반영됩니다.

## 🚀 실행 방법

### 웹 대시보드 실행
```bash
streamlit run app.py
```

### 자동 동기화 실행 (작업 스케줄러 등록용)
```bash
python auto_sync_sheets.py
```
*Tip: Windows 작업 스케줄러나 Linux Cron을 이용하여 매일 특정 시간에 실행되도록 등록하세요.*

---
개발 및 관련 문의: [작성자/부서명 입력]
