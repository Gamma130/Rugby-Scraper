from playwright.sync_api import sync_playwright
import pandas as pd
import json


def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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

        rows = page.locator('.sp-league-table tbody tr')
        count = rows.count()
        for i in range(count):
            Pos: str = rows.nth(i).locator('.data-rank').inner_text()
            Mannschaft = rows.nth(i).locator('.data-name').inner_text()
            Spiele = rows.nth(i).locator('.data-p').inner_text()
            Siege = rows.nth(i).locator('.data-w').inner_text()
            Niederlage = rows.nth(i).locator('.data-l').inner_text()
            Unentschiedien = rows.nth(i).locator('.data-d').inner_text()
            PKt_für = rows.nth(i).locator('.data-pf').inner_text()
            PKt_gegen = rows.nth(i).locator('.data-pa').inner_text()
            Spielerpkt_diff = rows.nth(i).locator('.data-pd').inner_text()
            Punkte = rows.nth(i).locator('.data-pts').inner_text()

            print(Mannschaft)
            standings.append({
                'Pos': Pos,
                'Mannschaft': Mannschaft,
                'Spiele': Spiele,
                'Siege': Siege,
                'Niederlage': Niederlage,
                'Unentschieden': Unentschiedien,
                'PKt_für': PKt_für,
                'PKt_gegen': PKt_gegen,
                'Spielerpkt_diff': Spielerpkt_diff,
                'Punkte': Punkte
            })

        browser.close()
        return pd.DataFrame(standings)


if __name__ == "__main__":
    if __name__ == "__main__":
        standings_df = scrape_rugby_matches("https://bits-rugby-ls.de/rugby-1-bundesliga-sued-west")
        standings_json = standings_df.to_json(orient='records', date_format='iso')

        # Save to file
        with open('standings-table-SW.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(standings_json), f, ensure_ascii=False, indent=2)
