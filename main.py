from playwright.sync_api import sync_playwright
import pandas as pd
import json


def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        matches = []

        # Go to the page and wait for iframe to load
        page.goto(url)
        close_cookies = page.locator('.cmplz-close')
        close_cookies.click()
        while True:
            current_table_page = page.locator('a.paginate_button.current').inner_text()
            rows = page.locator('tr.sp-row')
            count = rows.count()
            for i in range(count):
                date = rows.nth(i).locator('.data-date date').inner_text()
                teams = rows.nth(i).locator('.data-event').inner_text()
                score = rows.nth(i).locator('.data-time').inner_text()
                matchday = rows.nth(i).locator('.data-day').inner_text()

                match_link = rows.nth(i).locator('.data-event a')
                match_link.click()

                # Add longer wait time
                page.wait_for_selector('div.sp-section-content.sp-section-content-venue', timeout=30000)

                venue_selector = 'div > div.sp-section-content.sp-section-content-venue > div > table > thead > tr > th > a'
                venue = page.locator(venue_selector).inner_text()
                page.go_back()
                page.wait_for_selector('tr.sp-row')
                page.locator(f'a.paginate_button[data-dt-idx="{current_table_page}"]').click()
                page.wait_for_selector('tr.sp-row')
                matches.append({
                    'date': date,
                    'teams': teams,
                    'score': score,
                    'matchday': matchday,
                    'venue': venue
                })


            next_button = page.locator('a.paginate_button.next')
            if 'disabled' in page.locator('a.paginate_button.next').get_attribute('class'):
                break

            next_button.click()
            page.wait_for_selector('tr.sp-row')
        browser.close()
        return pd.DataFrame(matches)


if __name__ == "__main__":
    if __name__ == "__main__":
        matches_df = scrape_rugby_matches("https://bits-rugby-ls.de/rugby-1-bundesliga-sued-west")
        matches_json = matches_df.to_json(orient='records', date_format='iso')

        # Save to file
        with open('rugby_matches_SW.json', 'w', encoding='utf-8') as f:
            json.dump(json.loads(matches_json), f, ensure_ascii=False, indent=2)
