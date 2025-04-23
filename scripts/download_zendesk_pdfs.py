import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

BASE_URL = "https://vroozi.zendesk.com/hc/en-us"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def safe_name(name):
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name.strip()) or "Unnamed"

def download_pdf(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS)
        with open(save_path, "wb") as f:
            f.write(resp.content)
        print(f"      ✅ Downloaded: {os.path.basename(save_path)}")
    except Exception as e:
        print(f"      ❌ Failed to download {url}: {e}")

# Step 1: Get all category URLs
resp = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(resp.content, "html.parser")

category_links = {}
for a in soup.find_all("a", href=True):
    if "/categories/" in a["href"]:
        full_url = urljoin(BASE_URL, a["href"])
        name = safe_name(a.get_text())
        category_links[full_url] = name

print(f"Found {len(category_links)} categories.\n")

# Step 2: For each category
for category_url, category_name in category_links.items():
    print(f"📁 Category: {category_name}")
    try:
        cat_resp = requests.get(category_url, headers=HEADERS)
        cat_soup = BeautifulSoup(cat_resp.content, "html.parser")

        # Step 3: Find section URLs
        section_links = {}
        for a in cat_soup.find_all("a", href=True):
            if "/sections/" in a["href"]:
                full_url = urljoin(category_url, a["href"])
                name = safe_name(a.get_text())
                section_links[full_url] = name

        for section_url, section_name in section_links.items():
            print(f"  📂 Section: {section_name}")
            try:
                sec_resp = requests.get(section_url, headers=HEADERS)
                sec_soup = BeautifulSoup(sec_resp.content, "html.parser")

                article_links = set()
                for a in sec_soup.find_all("a", href=True):
                    if "/hc/en-us/articles/" in a["href"]:
                        article_links.add(urljoin(section_url, a["href"]))

                folder_path = os.path.join("vroozi_pdfs", category_name, section_name)
                os.makedirs(folder_path, exist_ok=True)

                for article_url in article_links:
                    try:
                        art_resp = requests.get(article_url, headers=HEADERS)
                        art_soup = BeautifulSoup(art_resp.content, "html.parser")

                        for a in art_soup.find_all("a", href=True):
                            if "article_attachments" in a["href"]:
                                pdf_url = urljoin(article_url, a["href"])
                                parsed = urlparse(pdf_url)
                                filename = a.string
                                if not filename.lower().endswith(".pdf"):
                                    filename += ".pdf"
                                save_path = os.path.join(folder_path, filename)
                                download_pdf(pdf_url, save_path)

                    except Exception as e:
                        print(f"    ❌ Error in article {article_url}: {e}")

            except Exception as e:
                print(f"  ❌ Error in section {section_url}: {e}")

    except Exception as e:
        print(f"❌ Error in category {category_url}: {e}")

print("\n🎉 All PDFs downloaded and organized by category/section.")