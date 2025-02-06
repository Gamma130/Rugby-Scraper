from playwright.sync_api import sync_playwright
import pandas as pd
import json


def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        standings = []

        # Go to the page and wait for iframe to load
        page.goto(url)
        try:
            close_cookies = page.locator('.cmplz-close')
            if close_cookies.is_visible(timeout=3000):
                close_cookies.click()
        except:
            pass

        rows = page.locator('.mui-h4dpb tbody tr')
        count = rows.count()
        for i in range(count):
            Club = rows.nth(i).locator('.mui-nqo5y4').inner_text()

            print(Club)
            standings.append({
            })

        browser.close()
        return pd.DataFrame(standings)


if __name__ == "__main__":
    if __name__ == "__main__":
        standings_df = scrape_rugby_matches("https://www.rugbydeutschland.org/1-bundesliga-sued-west-266851v4/leagues/9605/seasons/216")
        standings_json = standings_df.to_json(orient='records', date_format='iso')

        # Save to file
        with open('Standings-Table-SW.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(standings_json), f, ensure_ascii=False, indent=2)
