import json
import jsonlines
from typing import Dict, Any
from datetime import datetime

def save_to_jsonl(data: Dict[str, Any], filepath: str = "data/results.jsonl"):
    """
    데이터를 JSONL 파일에 추가(Append)합니다.
    """
    # 타임스탬프 추가
    if "saved_at" not in data:
        data["saved_at"] = datetime.now().isoformat()
        
    with jsonlines.open(filepath, mode='a') as writer:
        writer.write(data)
    
    print(f"[Saved] {data.get('title', 'No Title')[:30]}...")

