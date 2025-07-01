import time
import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
START_URL = "https://pragyan.nic.in"
ALLOWED_BASE_DOMAINS = ["pragyan.nic.in", "nicsi.nic.in", "nicsi.com"]
BLOCKED_DOMAINS = ["cloud.nicsi.in"]
OUTPUT_JSON = "company_data.json"

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === HELPERS ===
visited = set()
company_data = []

def get_visible_text(soup):
    for tag in soup(["script", "style", "noscript", "meta", "head", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def get_domain(url):
    return urlparse(url).netloc.lower()

def is_allowed_link(url, parent_url):
    domain = get_domain(url)
    parent_domain = get_domain(parent_url)

    if domain in BLOCKED_DOMAINS:
        return False
    if domain not in ALLOWED_BASE_DOMAINS:
        return False
    if domain == "pragyan.nic.in":
        return True
    if parent_domain == "pragyan.nic.in" and domain in ["nicsi.nic.in", "nicsi.com"]:
        return True
    return False

def get_all_links(page_source, current_url):
    soup = BeautifulSoup(page_source, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        if href:
            full_url = urljoin(current_url, href.split("#")[0])
            links.add(full_url)
    return links

def extract_numbers(text):
    # Extract lines that contain numbers for better data matching later
    lines = text.splitlines()
    important_lines = [line for line in lines if re.search(r"\b\d+\b", line)]
    return "\n".join(important_lines)

def scrape_page(url, parent_url=None):
    if url in visited:
        return
    try:
        domain = get_domain(url)
        from_domain = get_domain(parent_url or url)
        deep_crawl = domain == "pragyan.nic.in"

        print(f"[+] Visiting: {url}")
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        full_text = get_visible_text(soup)
        number_lines = extract_numbers(full_text)

        combined_content = f"{number_lines}\n\nFull Page Text:\n{full_text}".strip()

        company_data.append({
            "title": title,
            "content": combined_content
        })

        visited.add(url)

        if not deep_crawl:
            return

        links = get_all_links(html, url)
        for link in links:
            if link not in visited and is_allowed_link(link, url):
                scrape_page(link, parent_url=url)

    except Exception as e:
        print(f"[-] Error scraping {url}: {e}")

# === START ===
scrape_page(START_URL)

# === SAVE OUTPUT ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done. Scraped {len(company_data)} pages and saved to {OUTPUT_JSON}")
