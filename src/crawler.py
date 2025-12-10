import asyncio
from playwright.async_api import async_playwright, Page
from typing import List, Dict

class Crawler:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def crawl_reddit(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Reddit 검색 결과 크롤링"""
        results = []
        async with async_playwright() as p:
            # 브라우저 실행 시 봇 탐지 회피를 위한 아규먼트 추가
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York"
            )
            
            # navigator.webdriver 속성 제거 (봇 탐지 회피 핵심)
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = await context.new_page()
            
            # Reddit 검색 URL (New Sort)
            url = f"https://www.reddit.com/search/?q={keyword}&sort=new"
            print(f"[Reddit] Accessing: {url}")
            
            try:
                await page.goto(url, timeout=60000)
                
                # Debug mode: Wait for manual interaction (e.g. CAPTCHA)
                if not self.headless:
                    # 마우스 움직임 시뮬레이션 (사람처럼 보이게 하기)
                    try:
                        await page.mouse.move(100, 100)
                        await asyncio.sleep(0.5)
                        await page.mouse.down()
                        await asyncio.sleep(0.2)
                        await page.mouse.up()
                    except Exception:
                        pass
                        
                    print(f"[Debug] Browser is visible. Waiting 30s for manual interaction/loading...")
                    await asyncio.sleep(30)
                
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(3) # Wait for Dynamic content
                
                # Reddit UI Fallback Strategy
                # 1. shreddit-post (New UI)
                posts = []
                shreddit_posts = await page.locator("shreddit-post").all()
                if shreddit_posts:
                    print(f"[Reddit] Found {len(shreddit_posts)} 'shreddit-post' elements.")
                    posts = shreddit_posts
                else:
                    print("[Reddit] 'shreddit-post' not found. Trying fallback selectors...")
                    
                    # 2. Search Result Item Container (div > ... > h3 > a)
                    # Often Reddit search results are wrapped in a container that has a specific ID or class
                    # But reliable way is to find the headings.
                    
                    # Try finding headings that contain links (Post titles)
                    # This selector finds 'a' tags that are direct children of 'h3' or inside 'h3'
                    # Reddit search results usually use H3 for post titles
                    post_links = await page.locator("h3 > a").all()
                    
                    if not post_links and len(post_links) == 0:
                         # Try with 'h1' or 'h2' just in case
                         post_links = await page.locator("a[data-click-id='body']").all()

                    if post_links:
                         print(f"[Reddit] Found {len(post_links)} fallback title links.")
                         posts = post_links
                    else:
                         print("[Reddit] No fallback posts found. Dumping page title/content for debug.")
                         print(f"Page Title: {await page.title()}")

                print(f"[Reddit] Found {len(posts)} potential posts. Processing top {limit}...")
                
                for i, post in enumerate(posts):
                    if i >= limit: break
                    
                    try:
                        # Determine if 'post' is a container (shreddit-post) or a link (fallback)
                        tag_name = await post.evaluate("el => el.tagName.toLowerCase()")
                        
                        if tag_name == "shreddit-post":
                            title = await post.get_attribute("post-title")
                            link = await post.get_attribute("content-href")
                            author = await post.get_attribute("author")
                            content = await post.text_content()
                        elif tag_name == "a":
                            # It's the title link itself
                            title = await post.text_content()
                            link = await post.get_attribute("href")
                            
                            # Navigate up to find author or content if possible, but for now just get title/link
                            # Author is often in a sibling or parent's sibling. Hard to get reliably without container.
                            author = "Unknown (Fallback)"
                            content = title # Use title as content preview
                        else:
                             # Generic container
                            title = await post.text_content()
                            link = ""
                            author = "Unknown"
                            content = ""
                            
                        if link and not link.startswith("http"):
                            link = f"https://www.reddit.com{link}"

                        results.append({
                            "platform": "reddit",
                            "keyword": keyword,
                            "title": title.strip() if title else "No Title",
                            "url": link,
                            "author": author,
                            "content": content.strip()[:200] if content else "" 
                        })
                    except Exception as e:
                        print(f"[Reddit] Error parsing post {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"[Reddit] Crawling failed: {e}")
            finally:
                await browser.close()
                
        return results

    async def crawl_x(self, keyword: str, limit: int = 5) -> List[Dict]:
        """X (Twitter) 검색 결과 크롤링 - Temporarily disabled or minimized focus"""
        print("[X] Skipping X crawl as per instruction.")
        return []
