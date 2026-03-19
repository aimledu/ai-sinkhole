"""
collect_web_content.py

Experimental utilities for collecting structured content from publicly
accessible websites using an asynchronous crawler.

This module is designed to support downstream analysis pipelines such as
LLM-based website classification. Output format is intentionally stable
and text-based to preserve compatibility with existing consumers.

This is NOT a production crawler.
"""

# =========================
# Standard & Third-Party Imports
# =========================
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# =========================
# Global Configuration
# =========================
# Root directory for experiment artifacts and output data.
# All relative paths used in this module are resolved from this location.
EXPERIMENT_ROOT = Path.cwd()
COLLECTED_DATA_ROOT = EXPERIMENT_ROOT / "experiement_data" / "collected_website_data"
CRAWL_DELAY_SECONDS = 2

# =============================================================================
# Core Crawling Logic
# =============================================================================


async def collect_data_from_url(url_to_test):
    """
    Crawl a single webpage and extract high-level metadata and content.

    This function performs an asynchronous network request to retrieve
    webpage data, filters out non-relevant HTML elements, and returns
    a formatted string containing:
        - The source URL
        - Extracted metadata
        - Markdown-formatted webpage content

    Args:
        url_to_test (str): Fully qualified URL of the webpage to crawl.

    Returns:
        str: Serialized webpage data containing URL, metadata, and markdown.

    Notes:
        - This function relies on the crawl4ai library.
        - See https://docs.crawl4ai.com/core/crawler-result/ for details.
    """
    crawling_config = CrawlerRunConfig(
        excluded_tags=["script", "style"],
        keep_data_attributes=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url_to_test,
            config=crawling_config,
        )
        # Combine relevant crawl outputs into a single serialized string
        web_page_info = " ".join(
            (
                f"URL: {url_to_test}",
                f"metadata: {result.metadata}",
                f"webpage_content: {result.markdown}",
                # f"webpage_html: {result.cleaned_html}",  # Optional raw HTML output
            )
        )

        return web_page_info


async def collect_and_optionally_save(url_to_test, log_dir=None):
    """
    Orchestrate webpage data collection and optionally persist results to disk.

    This function:
        - Measures execution time for a single crawl
        - Prints results to stdout when no log directory is provided
        - Writes crawl output to a timestamped JSON file when logging is enabled

    Args:
        url_to_test (str): Fully qualified URL of the webpage to crawl.
        log_dir (str, optional): Subdirectory name for storing crawl results.
            If None, results are printed instead of saved.


    """
    start_time = time.time()
    result = await collect_data_from_url(url_to_test)
    duration = time.time() - start_time

    if log_dir is None:
        # Interactive / debug mode output
        print("***" * 7)
        print(result)
        print(f"[INFO] Crawl completed in {duration:.2f}s")
    else:
        # Persist crawl output to a timestamped JSON file
        output_dir = COLLECTED_DATA_ROOT / log_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        domain = urlparse(url_to_test).netloc.replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.json"

        full_file_path = output_dir / filename
        try:
            # print(folder_path.absolute())
            with open(full_file_path, "w", encoding="utf-8") as f:
                json.dump(result, f)
        except Exception as e:
            # Fail gracefully if the file cannot be written
            print(f"[ERROR] Failed to write crawl output: {e}")
            return
        print(f"[INFO] Saved crawl result → {full_file_path}")
        print(f"[INFO] Crawl duration: {duration:.2f}s")


# =============================================================================
# Batch Processing
# =============================================================================
def load_url_list(json_path: Path):
    """
    Load a list of URLs from a JSON file.

    Args:
        json_path (Path): Path to JSON file.

    Returns:
        list[str]: List of URLs.
    """
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("URL list JSON must contain a list of strings")

    return data


def crawl_url_batch(url_list_path, output_subdir):
    """
    Sequentially crawl URLs from a JSON file with basic rate limiting.

    Args:
        url_list_path (str): Relative path to JSON file containing URLs.
        output_subdir (str): Output folder under collected data root.
    """
    full_path = EXPERIMENT_ROOT / url_list_path
    urls = load_url_list(full_path)
    for index, website_url in enumerate(urls, start=1):
        # Progress indicator for batch crawling
        print("=" * 80)
        print(f"[{index}/{len(urls)}] Crawling: {website_url}")
        asyncio.run(collect_and_optionally_save(website_url, output_subdir))
        # Throttle requests to avoid overwhelming target websites
        time.sleep(CRAWL_DELAY_SECONDS)
    return


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    """
    Command-line entry point for interactive execution.

    Users can select between:
        0 - Crawl a single URL entered manually
        1 - Crawl a predefined list of non-LLM-related websites
        2 - Crawl a predefined list of LLM-related websites
    """
    choice = input(
        "Select operation mode:\n"
        "0 - Test crawling a single URL\n"
        "1 - Crawl non-LLM sample websites\n"
        "2 - Crawl LLM sample websites\n"
        "> "
    )
    if choice == "0":
        url_to_test = input("Enter URL (e.g. https://wikipedia.org): ").strip()
        asyncio.run(collect_and_optionally_save(url_to_test))

    elif choice == "1":  # non-llm urls
        # Crawl sample websites not directly related to LLM services
        list_of_urls = "dataset/list_of_non_ai_services.json"
        website_log_folder = "non_LLM_website_data/"
        crawl_url_batch(list_of_urls, website_log_folder)
    elif choice == "2":  # llm urls
        # Crawl sample websites offering LLM-based services
        list_of_urls = "dataset/list_of_ai_services.json"
        website_log_folder = "LLM_website_data/"

        crawl_url_batch(list_of_urls, website_log_folder)
    else:
        # No operation selected
        print("[INFO] No valid option selected. Exiting.")
