import asyncio
import argparse
from src.crawler import Crawler
from src.verifier import verify_post
from src.utils import save_to_jsonl

async def main(keyword: str, platform: str, limit: int, headless: bool):
    print(f"🚀 Starting crawler for keyword: '{keyword}' on {platform}...")
    
    crawler = Crawler(headless=headless)
    posts = []

    # 1. Crawl
    if platform in ["reddit", "all"]:
        reddit_posts = await crawler.crawl_reddit(keyword, limit)
        posts.extend(reddit_posts)
    
    if platform in ["twitter", "x", "all"]:
        x_posts = await crawler.crawl_x(keyword, limit)
        posts.extend(x_posts)
    
    print(f"\n🔎 Verifying {len(posts)} posts with LLM...")
    
    # 2. Verify & Save
    for post in posts:
        # LLM 검증
        verification = verify_post(post, keyword)
        
        if verification.get("is_relevant"):
            # 검증 결과 병합
            post.update(verification)
            save_to_jsonl(post)
            print(f"✅ Verified & Saved: {post['url']}")
        else:
            print(f"❌ Skipped: {post['url']} (Reason: {verification.get('reason')})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Goods Trading Crawler CLI")
    parser.add_argument("--keyword", type=str, required=True, help="Search keyword (e.g., '아이유 포카 양도')")
    parser.add_argument("--platform", type=str, default="all", choices=["reddit", "x", "twitter", "all"], help="Target platform")
    parser.add_argument("--limit", type=int, default=5, help="Number of posts to crawl per platform")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in visible mode (for debugging)")

    args = parser.parse_args()
    
    # Run async main
    asyncio.run(main(
        keyword=args.keyword, 
        platform=args.platform, 
        limit=args.limit,
        headless=not args.no_headless
    ))

