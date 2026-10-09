"""Processing pipeline tying the scraper and config loader together.

Demo purpose: gives the call graph real cross-file edges (main pipeline
calling into both other modules), and includes one orphaned function
never called anywhere - useful for demonstrating the orphaned-functions
panel alongside the worst-case CRS score.
"""
from data_scraper import scrape_batch, save_raw_html
from config_loader import load_config, apply_dynamic_setting


def run_pipeline(urls, config_path):
    config = load_config(config_path)
    results = scrape_batch(urls)
    for i, result in enumerate(results):
        save_raw_html(urls[i], f"page_{i}.html")
    return apply_dynamic_setting(config)


def unused_debug_helper():
    """Never called anywhere - orphaned function for the demo."""
    print("debug helper - not wired up")
