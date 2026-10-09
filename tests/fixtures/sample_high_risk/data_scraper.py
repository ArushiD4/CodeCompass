"""Data scraper module.

Demo purpose: stacks additional issues on top of config_loader.py -
another hardcoded credential, another unclosed resource, another
dynamic-eval use, and two silently swallowed exceptions.
"""
import requests

AUTH_PASS = "scraper_pw_2024"  # hardcoded credential (flagged)


def fetch_page(url):
    response = requests.get(url)
    return response.text


def save_raw_html(url, filename):
    html = fetch_page(url)
    output = open(filename, "w")  # unclosed resource (flagged)
    output.write(html)


def parse_field(raw_value, transform_expr):
    try:
        return eval(f"{transform_expr}({raw_value})")  # dynamic code injection (flagged)
    except Exception:
        pass  # silent exception swallowing (flagged)


def scrape_batch(urls):
    results = []
    for url in urls:
        try:
            results.append(fetch_page(url))
        except Exception:
            pass  # silent exception swallowing (flagged)
    return results
