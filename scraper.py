"""GitHubのGoogle組織のリポジトリ一覧ページをスクレイピングする。

GitHub API は使わず、ブラウザで見るのと同じ一覧ページ
（https://github.com/orgs/google/repositories）のHTMLを取得して解析する。
一覧ページのHTMLには、画面の表示に使うデータが
<script data-target="react-app.embeddedData"> の中にJSONで埋め込まれているので、
BeautifulSoupでそのタグを取り出して、リポジトリ名・主要な言語・スター数を読む。
"""

import json
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://github.com/orgs/google/repositories"
HEADERS = {"User-Agent": "Mozilla/5.0 (s2622037 DS Programming scraping assignment)"}


MAX_RETRIES = 5


def fetch_page(page: int) -> str:
    """一覧ページの page ページ目のHTMLを返す。アクセスの前に必ず1秒待つ。

    アクセスが多すぎる（HTTP 429）・サーバー側のエラー（5xx）のときは、
    待ち時間を延ばしながら最大 MAX_RETRIES 回までやり直す。
    """
    # q=sort:name-asc で名前順に並べる（更新順だと巡回中に順番が変わり、取りこぼしが出るため）
    params = {"q": "sort:name-asc", "page": page}
    for attempt in range(1, MAX_RETRIES + 1):
        time.sleep(1)
        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 30 * attempt
            print(f"  HTTP {response.status_code}: {wait} 秒待ってやり直します（{attempt}/{MAX_RETRIES}）")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.text
    raise RuntimeError(f"{page} ページ目を取得できませんでした")


def parse_page(html: str) -> tuple[list[dict], int]:
    """HTMLからリポジトリの一覧と総ページ数を取り出す。"""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", attrs={"data-target": "react-app.embeddedData"})
    if script is None:
        raise ValueError("リポジトリ一覧のデータが見つかりません（ページの構造が変わった可能性があります）")

    data = json.loads(script.string)["payload"]["orgReposPageRoute"]
    repos = []
    for item in data["repositories"]:
        language = item.get("primaryLanguage")
        repos.append(
            {
                "name": item["name"],
                "language": language["name"] if language else None,
                "stars": item["starsCount"],
            }
        )
    return repos, data["pageCount"]


def scrape_all() -> list[dict]:
    """全ページを巡回して、全リポジトリの情報を返す。"""
    all_repos = []
    page = 1
    page_count = 1
    while page <= page_count:
        html = fetch_page(page)
        repos, page_count = parse_page(html)
        all_repos.extend(repos)
        print(f"{page}/{page_count} ページ目: {len(repos)} 件取得（累計 {len(all_repos)} 件）")
        page += 1
    return all_repos


if __name__ == "__main__":
    for repo in scrape_all()[:10]:
        print(repo)
