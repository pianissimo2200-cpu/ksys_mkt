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
    """선택된 모델(Gemini 또는 GPT)을 사용하여 경쟁사 본문을 분석하고 자사 맞춤형 포스팅을 생성합니다."""
    if not api_key:
        return f"{model_type.upper()} API 키가 입력되지 않았습니다."
        
    prompt = f"""
다음은 우리 회사의 경쟁사가 작성한 최근 블로그 포스팅 본문입니다.

[경쟁사 블로그 본문]
{content}

[우리의 포지셔닝/강조점]
{company_positioning}

위 경쟁사 글을 먼저 분석하여, 그들이 강조하는 메인 키워드와 마케팅 소구점(Selling Point)이 무엇인지 파악하세요.
그 후, 경쟁사의 논리를 부드럽게 반박하거나 우리 제품의 우수성({company_positioning})을 더 부각시킬 수 있는 네이버 블로그용 포스팅 초안을 작성해주세요.
글은 서론-본론-결론이 명확하게 구분되어야 하며, 적절한 이모지와 해시태그를 포함해야 합니다. SEO(검색엔진 최적화)를 고려하여 자연스럽게 작성해주세요.

결과는 다음 포맷으로 출력해주세요:

---
## 📊 경쟁사 분석 요약
(경쟁사 글에 대한 3줄 요약 및 분석)

---
## 📝 자동 생성된 포스팅 초안
(작성된 블로그 포스팅 내용)
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
                model="gpt-4o", # 가장 최신 모델인 gpt-4o 사용
                messages=[
                    {"role": "system", "content": "너는 전문적인 블로그 마케팅 전문가이자 카피라이터야."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GPT 텍스트 생성 중 오류 발생: {e}"


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
