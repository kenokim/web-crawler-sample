import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def verify_post(post_data: dict, keyword: str) -> dict:
    """
    Gemini LLM을 사용하여 게시글이 키워드에 맞는 판매/양도 글인지 검증합니다.
    """
    
    # JSON 형식 출력을 유도하기 위한 구체적인 프롬프트
    prompt = f"""
    You are a specialized trade post verifier.
    Determine if the following post is a valid selling/trading post for the item: "{keyword}".
    Ignore 'Buying' (WTB) requests. Focus on 'Selling' (WTS) or 'Trading' (WTT).
    
    [Post Data]
    Title: {post_data.get('title', '')}
    Content: {post_data.get('content', '')}
    
    Respond with a valid JSON object only. Do not add any Markdown formatting (no ```json or ```).
    JSON structure:
    {{
        "is_relevant": boolean, 
        "reason": "short explanation",
        "price": "extracted price if available, else null",
        "item_name": "normalized item name if found"
    }}
    """

    try:
        # 모델명 수정 (gemini-1.5-flash -> gemini-pro 또는 gemini-1.5-flash-latest)
        # 안정성을 위해 gemini-pro 사용 권장, 혹은 flash 사용 시 최신 이름 확인 필요
        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result_text = response.text
        return json.loads(result_text)
        
    except Exception as e:
        print(f"[Verifier Error] {e}")
        return {"is_relevant": False, "reason": f"Error during verification: {e}", "price": None}
