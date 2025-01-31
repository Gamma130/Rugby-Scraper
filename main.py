from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_rugby_matches():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        matches = []

        # Go to the page and wait for iframe to load
        page.goto("https://bits-rugby-ls.de/rugby-1-bundesliga-nord-ost")
        close_cookies = page.locator('.cmplz-close')
        close_cookies.click()
        while True:
            current_table_page = page.locator('a.paginate_button.current').inner_text()
            print('current page: ', current_table_page)
            rows = page.locator('tr.sp-row')
            count = rows.count()
            print(count)
            for i in range(count):
                print(i)
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
            time.sleep(2)
        browser.close()
        df = pd.DataFrame(matches)
        print(df)


if __name__ == "__main__":
    scrape_rugby_matches()