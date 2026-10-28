import argparse
import csv
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.mobiledokan.co"
DEFAULT_BRANDS = [
    "apple", "samsung", "xiaomi", "oppo", "vivo", "realme", "honor",
    "motorola", "nokia", "tecno", "infinix", "itel", "tcl",
]
LIMIT = None
TOTAL_PAGES = 60
DELAY = 1.5
OUTPUT = ROOT / "data" / "raw" / "phones_crawled.csv"


def fetch_soup(session, url):
    response = session.get(url, timeout=25)
    time.sleep(DELAY)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def collect_urls(session, brands=None):
    urls = set()
    for brand in (brands or DEFAULT_BRANDS):
        url = f"{BASE}/brand/{brand}/"
        pages = 0
        visited = set()
        while url and url not in visited and pages < TOTAL_PAGES:
            visited.add(url)
            try:
                soup = fetch_soup(session, url)
                links = soup.select(".aps-product-title a[href]")
                if not links:
                    raise ValueError("Không tìm thấy liên kết sản phẩm trong danh mục.")
                for link in links:
                    target = urlsplit(urljoin(url, link["href"]))
                    if (target.scheme == "https"
                            and target.netloc in {"www.mobiledokan.co", "mobiledokan.co"}
                            and target.path.startswith("/product/")):
                        urls.add(f"{BASE}{target.path.rstrip('/')}/")
                next_link = soup.select_one('a.next.page-numbers[href], a[rel="next"][href]')
                next_url = urljoin(url, next_link["href"]) if next_link else None
                url = (next_url if next_url
                       and next_url.startswith(f"{BASE}/brand/{brand}/page/") else None)
            except (requests.RequestException, ValueError) as exc:
                print(f"Lỗi danh mục {brand}: {exc}", flush=True)
                break
            pages += 1
            print(f"Đã gom {len(urls)} URL", flush=True)
    return urls


def read_raw_product(soup, url):
    heading = soup.select_one("h1.aps-main-title")
    groups = soup.select("#aps-specs .aps-group")
    if heading is None or not groups:
        raise ValueError("Không tìm thấy tên hoặc bảng thông số sản phẩm.")
    price = soup.select_one(".aps-feature-price-list")
    row = {
        "URL": url,
        "Ten_may": heading.get_text(" ", strip=True),
        "Gia_ban": price.get_text(" ", strip=True) if price else "",
    }
    for group in groups:
        title = group.select_one(".aps-group-title")
        if title is None:
            continue
        section = title.get_text(" ", strip=True)
        for tr in group.select("table.aps-specs-table tr"):
            label = tr.select_one(".aps-attr-title")
            value = tr.select_one(".aps-attr-value")
            if label is None or value is None:
                continue
            key = f'{section}.{label.get_text(" ", strip=True)}'
            text = value.get_text(" ", strip=True)
            row[key] = row[key] + "\n" + text if key in row else text
    return row


def crawl_phones(session, urls, rows, limit=LIMIT):
    for url in sorted(urls):
        if limit is not None and len(rows) >= limit:
            break
        try:
            row = read_raw_product(fetch_soup(session, url), url)
            rows.append(row)
            print(f'{len(rows)}/{limit or len(urls)}: {row["Ten_may"]}', flush=True)
        except (requests.RequestException, ValueError) as exc:
            print(f"Bỏ qua {url}: {exc}", flush=True)


def save_csv(rows, path=OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(
        ["URL", "Ten_may", "Gia_ban"] + [key for row in rows for key in row]
    ))
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Đã lưu {len(rows)} máy vào {path}")


def main():
    ap = argparse.ArgumentParser(description="Cào thông số điện thoại từ MobileDokan")
    ap.add_argument("--brands", help="Danh sách hãng, cách nhau bằng dấu phẩy (mặc định: tất cả)")
    ap.add_argument("--limit", type=int, default=LIMIT, help="Số máy tối đa (mặc định: không giới hạn)")
    ap.add_argument("--out", type=Path, default=OUTPUT, help="File CSV đầu ra")
    args = ap.parse_args()
    brands = [b.strip().lower() for b in args.brands.split(",")] if args.brands else None
    rows = []
    with requests.Session() as session:
        session.headers.update({"User-Agent": "PhoneSpecsResearch/1.0"})
        try:
            crawl_phones(session, collect_urls(session, brands), rows, args.limit)
        except KeyboardInterrupt:
            print("Đã dừng")
        finally:
            save_csv(rows, args.out)


if __name__ == "__main__":
    main()
