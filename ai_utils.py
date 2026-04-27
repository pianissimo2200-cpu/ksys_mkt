import google.generativeai as genai
from openai import OpenAI
import os

def validate_gemini_key(api_key):
    if not api_key: return False, "키를 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        # 특정 모델을 찾는 대신, 사용 가능한 모델 목록을 호출할 수 있는지 확인합니다.
        # 이것이 성공하면 키가 유효하고 권한이 있는 것입니다.
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return True, "유효한 키입니다."
        return False, "유효한 키이나, 사용 가능한 모델을 찾을 수 없습니다."
    except Exception as e:
        return False, f"유효하지 않거나 권한이 없는 키입니다. (상세 에러: {str(e)})"

def validate_openai_key(api_key):
    if not api_key: return False, "키를 입력해주세요."
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True, "유효한 키입니다."
    except Exception as e:
        return False, "유효하지 않거나 권한이 없는 키입니다."

def analyze_and_generate_post(content, company_positioning, api_key, model_type='gemini'):
    """선택된 모델(Gemini 또는 GPT)을 사용하여 경쟁사 본문을 분석하고 케이시스만의 벤치마킹 포인트와 포스팅을 생성합니다."""
    if not api_key:
        return f"{model_type.upper()} API 키가 입력되지 않았습니다."
        
    prompt = f"""
다음은 우리 회사의 경쟁사가 작성한 최근 블로그 포스팅 본문입니다.

[경쟁사 블로그 본문]
{content}

[우리의 포지셔닝/강조점]
{company_positioning}

위 경쟁사 글을 정밀 분석하여 다음 3가지 관점으로 내용을 정리하고, 우리가 이길 수 있는 새로운 포스팅 초안을 작성해주세요.

1. [벤치마킹 포인트] 경쟁사 글에서 우리가 부러워할 만한 점이나 배울 점은 무엇인가? (구체적으로 2~3가지)
2. [케이시스만의 차별화 전략] 경쟁사의 논리를 어떻게 우리만의 강점({company_positioning})으로 압도할 것인가?
3. [실전 가이드] 경쟁사보다 더 높은 상위 노출과 클릭을 끌어내기 위한 핵심 팁

결과는 다음 포맷으로 출력해주세요:

---
## 🎯 벤치마킹 어드바이저 리포트
### 1. 우리가 배울 점 (Point of Envy)
(내용 작성)

### 2. 케이시스만의 필승 전략 (Ksys Advantage)
(내용 작성)

### 3. 포스팅 핵심 가이드
(내용 작성)

---
## 📝 케이시스 맞춤형 포스팅 초안
(작성된 블로그 포스팅 내용 - 서론/본론/결론, 이모지, 해시태그 포함)
"""

    if model_type == 'gemini':
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"제미나이 텍스트 생성 중 오류 발생: {e}"
            
    elif model_type == 'gpt':
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "너는 LED 전광판 전문 마케팅 컨설턴트이자 카피라이터야."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GPT 텍스트 생성 중 오류 발생: {e}"

def generate_led_keywords(api_key, model_type='gemini'):
    """LED 전광판과 관련하여 선점하기 좋은 업종별/문제해결형/트렌드 키워드와 제목을 제안합니다."""
    if not api_key:
        return "API 키가 필요합니다."
        
    prompt = """
너는 LED 전광판 전문 마케팅 전략가야. 우리 회사(케이시스)가 네이버 블로그에서 선점하기 좋은 'LED 전광판' 관련 키워드를 발굴해서 제안해줘.

다음 3가지 카테고리별로 각 3개씩, 총 9개의 키워드 세트를 제안해줘.

1. [업종별 침투] LED 전광판이 필요한 특정 장소/업종 타겟 (예: 교회, 학교, 경로당 등)
2. [문제 해결 및 정보] 고객의 고민이나 궁금증 해결 (예: 가격 비교, 유지보수, 설치 절차 등)
3. [시즌 및 트렌드] 현재 사회 분위기나 특정 시기에 맞는 키워드

각 키워드에 대해 다음을 포함해줘:
- 추천 키워드
- 선정 이유 (왜 지금 이 키워드를 선점해야 하는가?)
- 추천 포스팅 제목 (사람들이 클릭하고 싶게 만드는 매력적인 제목)

출력은 깔끔한 마크다운 형식으로 해줘.
"""

    if model_type == 'gemini':
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"오류 발생: {e}"
    else:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"오류 발생: {e}"


def generate_blog_image(topic_summary, openai_api_key):
    """OpenAI DALL-E 3를 사용하여 블로그 썸네일 이미지를 생성합니다."""
    if not openai_api_key:
        return None, "OpenAI API 키가 입력되지 않았습니다."
        
    try:
        client = OpenAI(api_key=openai_api_key)
        
        prompt = f"A professional and highly engaging blog thumbnail image about: {topic_summary}. The image should be modern, clean, and suitable for a corporate technology or business blog. No text in the image."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url, None
    except Exception as e:
        return None, f"이미지 생성 중 오류 발생: {e}"
