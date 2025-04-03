import json
import os
from typing import List, Set, Tuple, Dict, Any
import uuid

from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CacheMode,
    BrowserConfig,
    LLMExtractionStrategy,
)
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.models import TokenUsage

from models.team import Team
from utils.data_utils import is_complete_venue, is_duplicate_venue
from config import CSS_SELECTOR, REQUIRED_KEYS


def get_browser_config() -> BrowserConfig:
    """Get browser configuration for web scraping."""
    return BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=True,  # Enable verbose logging
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """Get LLM strategy for data extraction."""
    api_token = os.getenv("GROQ_API_KEY")
    if not api_token:
        raise ValueError("GROQ_API_KEY no está configurada en el archivo .env")

    return LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",  # Volvemos al modelo original de Groq
        api_token=api_token,
        schema=Team.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract all hockey standings from the following HTML content. "
            "For each team, return an object with the following keys: "
            "'Pos' (position), 'Club' (team name), 'Pts' (points), 'PJ' (matches played), "
            "'PG' (matches won), 'PE' (drawn), 'PP' (lost), 'SP' (no points), "
            "'GF' (goals for), 'GC' (goals against), 'DG' (goal difference), "
            "'Bo' (bonus), 'Sa' (sanction), 'Logo' (URL of team logo)"
            "Ignore headers or decoration rows and extract only valid rows containing team data. "
            "Make sure to extract all numeric values as strings."
        ),
        input_format="markdown",
        verbose=True
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    # Fetch the page without any CSS selector or extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
            page_timeout=30000,  # Increase the timeout for this check
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    categoria: str,
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Fetch and process a page to extract hockey standings data.
    
    Args:
        crawler: AsyncWebCrawler instance
        base_url: URL to fetch
        css_selector: CSS selector for the table
        llm_strategy: LLM strategy for extraction
        session_id: Session ID for the crawler
        required_keys: List of required keys in the data
        categoria: Category name for the data
        
    Returns:
        Tuple of (list of teams, whether no results were found)
    """
    try:
        # Fetch the page
        print(f"🔎 Fetching hockey matches from: {base_url}")
        result = await crawler.arun(
            url=base_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=llm_strategy,
                css_selector=css_selector,
                session_id=session_id
            )
        )
        
        if not result.success:
            print(f"❌ Failed to fetch page: {result.error_message}")
            return [], True

        if not result.extracted_content:
            print("❌ No se pudo extraer contenido")
            return [], True

        # Process the extracted content
        teams = []
        try:
            extracted_data = json.loads(result.extracted_content)
            for item in extracted_data:
                # Ensure all required keys are present
                if not all(key in item for key in required_keys):
                    print(f"⚠️ Item missing required keys: {item}")
                    continue
                    
                # Add categoria to each team
                item["categoria"] = categoria
                
                # Ensure all numeric values are strings
                for key in ["posicion", "pj", "pg", "pe", "pp", "gf", "gc", "dif", "pts"]:
                    if key in item:
                        item[key] = str(item[key])
                
                teams.append(item)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return [], True

        return teams, False

    except Exception as e:
        print(f"❌ Failed to fetch page: {str(e)}")
        return [], True
