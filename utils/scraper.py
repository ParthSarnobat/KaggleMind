import os
import re  
from firecrawl import Firecrawl
import kagglehub
from dotenv import load_dotenv

load_dotenv()

def extract_comp_slug(url: str) -> str:
    """
    Extracts the true Kaggle competition identifier cleanly.
    Handles sub-tabs (/discussion, /data, /rules) and URL tracking queries.
    """
    #Strip off browser query params (everything after '?') and trailing slashes
    clean_url = url.split('?')[0].rstrip('/')
    
    match = re.search(r'/(?:competitions|c)/([^/]+)', clean_url)
    if match:
        return match.group(1)
        
    #Safe fallback if the URL structure is unexpected
    return clean_url.split('/')[-1]


def kaggle_summary(url):
    """
    Fetches the raw markdown from the competition page and technical metadata.
    """
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if firecrawl_api_key is None:
        raise ValueError("FIRECRAWL_API_KEY environment variable is required")

    app = Firecrawl(api_key=firecrawl_api_key)
    
    comp_slug = extract_comp_slug(url)
    
    print(f"Scraper: Fetching overview for competition folder: '{comp_slug}'...")
    
    scrape_result = app.scrape(url, formats=['markdown'])
    
    if isinstance(scrape_result, dict):
        markdown_content = scrape_result.get('markdown', 'No content found')
    else:
        markdown_content = getattr(scrape_result, 'markdown', 'No content found')
    
    # Safety guard: Truncate extreme markdown lengths to save token budget
    if len(markdown_content) > 60000:
        markdown_content = markdown_content[:60000] + "\n\n[Content truncated by scraper for size]"
    
    return {
        "slug": comp_slug,
        "markdown": markdown_content,
        "url": url
    }