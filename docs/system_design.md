# Goods Trading Crawler System Design

## 1. 개요 (Overview)
본 프로젝트는 **Reddit**과 **X (구 Twitter)** 에서 특정 굿즈 거래 글을 **Playwright**로 수집하고, **LLM (Large Language Model)** 을 통해 사용자가 원하는 매물인지 검증하여 **JSONL** 파일로 저장하는 시스템입니다.

## 2. 기술 스택 (Tech Stack)

### 2.1. 언어 및 런타임
- **Python 3.10+**

### 2.2. 핵심 라이브러리
| 역할 | 라이브러리 | 설명 |
|---|---|---|
| **웹 크롤링 (통합)** | `playwright` | Reddit 및 X의 검색 결과 페이지를 브라우저 환경에서 렌더링하여 데이터 추출. |
| **데이터 검증** | `openai` or `anthropic` | 수집된 텍스트가 실제 판매 글인지, 찾는 물건이 맞는지 판별. (비용 절감을 위해 Local LLM 사용 가능) |
| **데이터 저장** | `jsonlines` | 검증된 데이터를 JSONL 포맷으로 저장 (Append-only). |
| **스케줄링** | `APScheduler` | 주기적 실행. |
| **설정 관리** | `python-dotenv` | 환경 변수 관리. |

## 3. 시스템 아키텍처 (Architecture)

```mermaid
graph TD
    User[사용자 입력 (키워드)] --> Scheduler[작업 스케줄러]
    
    Scheduler --> Crawler[통합 수집기 (Playwright)]
    
    Crawler -- Reddit 검색 --> RedditPage[Reddit 검색 결과]
    Crawler -- X 검색 --> TwitterPage[X 검색 결과]
    
    RedditPage --> RawData[원본 데이터 추출]
    TwitterPage --> RawData
    
    RawData --> LLM[LLM 검증기]
    
    LLM -- 적합 (Relevant) --> JSONL[(결과 파일 .jsonl)]
    LLM -- 부적합 (Irrelevant) --> Discard[폐기]
```

## 4. 상세 설계

### 4.1. 수집기 (Playwright Crawler)

#### 공통 로직
- **입력**: 검색 키워드 리스트 (예: ["아이유 포카 양도", "NCT photocard WTS"])
- **브라우저 설정**: `headless=True` (디버깅 시 False), `stealth` 모드 적용 권장.

#### A. Reddit (Playwright)
- **URL**: `https://www.reddit.com/search/?q={keyword}&sort=new`
- **동작**:
  1. 검색 결과 페이지 로드.
  2. `shreddit-post` 또는 게시글 컨테이너 식별.
  3. 제목, 링크, 작성자, 미리보기 텍스트 추출.

#### B. X (Playwright)
- **URL**: `https://x.com/search?q={keyword}&f=live` (최신 탭)
- **동작**:
  1. 로그인 (쿠키/세션 활용 권장).
  2. 검색 페이지 로드 및 스크롤 다운.
  3. `article` 태그 내 트윗 텍스트, ID, 시간 추출.

### 4.2. 데이터 검증 (LLM Verifier)

수집된 원본 텍스트(제목+본문)를 LLM에 전송하여 필터링합니다.

- **프롬프트 예시**:
  ```text
  다음 게시글이 "{target_item}"의 "판매/양도" 글인지 판단해줘.
  구매(WTB) 글이나 교환(WTT) 글은 제외해.
  
  [게시글 정보]
  제목: ...
  내용: ...
  
  출력 포맷(JSON): {"is_selling": true, "item_match": true, "price": "10000원", "reason": "..."}
  ```

### 4.3. 데이터 저장 (JSONL Output)

검증을 통과한 데이터만 `results.jsonl` 파일에 추가(Append)합니다.

**JSON 구조:**
```json
{
  "platform": "reddit",
  "id": "post_id_123",
  "keyword": "search_keyword",
  "title": "Sale Post Title",
  "content": "Full content text...",
  "url": "https://...",
  "price": "extracted_price",
  "crawled_at": "2023-10-27T10:00:00"
}
```

## 5. 실행 흐름 (Workflow)

1. **설정 로드**: 키워드 리스트 및 LLM API 키 로드.
2. **크롤링 루프**:
   - 키워드별로 Playwright 브라우저 실행.
   - Reddit/X 검색 결과 페이지 파싱.
   - 최근 N개 게시글 추출.
3. **검증 및 저장**:
   - 추출된 게시글을 LLM API로 전송.
   - `is_selling` && `item_match`가 True인 경우 JSONL 파일에 한 줄씩 기록.
4. **종료 및 대기**: 지정된 간격(예: 10분) 후 재실행.

## 6. 프로젝트 구조

```
project_root/
├── data/
│   └── results.jsonl       # 결과 저장 파일
├── src/
│   ├── crawler.py          # Playwright 크롤링 로직
│   ├── verifier.py         # LLM 검증 로직
│   └── utils.py            # 파일 저장 등 유틸리티
├── main.py                 # 실행 진입점
├── .env                    # 환경변수
└── requirements.txt
```
