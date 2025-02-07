import time
import math
from playwright.sync_api import sync_playwright
import pandas as pd
import json


def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        standings = []

        # Go to the page and wait for content to load
        page.goto(url)
        try:
            page.wait_for_selector('.s50-cookie-banner__button-outlined button', timeout=3000)
            close_cookies = page.locator('.s50-cookie-banner__button-outlined button')
            if close_cookies.is_visible(timeout=3000):
                close_cookies.click()
        except:
            pass



        # Get all text elements that could be either Spieltag headers or scores
        elements = page.locator('tbody tr').all()

        for i, element in enumerate(elements):
            print(i)
            standing = element.locator('td:first-child .MuiTypography-root').text_content().strip().rstrip('.')
            club = element.locator('td.body .MuiTypography-root').nth(1).text_content().strip()
            points = element.locator('td.body .MuiTypography-root').nth(2).text_content().strip()
            games = element.locator('td.body .MuiTypography-root').nth(3).text_content().strip()
            Win = element.locator('td.body .MuiTypography-root').nth(4).text_content().strip()
            U = element.locator('td.body .MuiTypography-root').nth(5).text_content().strip()
            v = element.locator('td.body .MuiTypography-root').nth(6).text_content().strip()
            points_made = element.locator('td.body .MuiTypography-root').nth(7).text_content().strip()
            points_conceded = element.locator('td.body .MuiTypography-root').nth(8).text_content().strip()
            tries_scored = element.locator('td.body .MuiTypography-root').nth(10).text_content().strip()
            tries_conceded = element.locator('td.body .MuiTypography-root').nth(11).text_content().strip()
            offensive_bonus = element.locator('td.body .MuiTypography-root').nth(12).text_content().strip()
            defensive_bonus = element.locator('td.body .MuiTypography-root').nth(13).text_content().strip()

            print(club)
            standings_data = {
                'standing': standing,
                'club': club,
                'points': points,
                'Win': Win,
                'U': U,
                'v': v,
                'points_made': points_made,
                'points_conceded': points_conceded,
                'tries_scored': tries_scored,
                'tries_conceded': tries_conceded,
                'offensive_bonus': offensive_bonus,
                'defensive_bonus': defensive_bonus
            }

            standings.append(standings_data)
        browser.close()
        return pd.DataFrame(standings)


if __name__ == "__main__":
    matches_df = scrape_rugby_matches("https://www.rugbydeutschland.org/1-bundesliga-sued-west-266851v4/leagues/9605/seasons/216")
    print(matches_df)  # Print to verify the output
    matches_json = matches_df.to_json(orient='records', date_format='iso')

    # Save to file
    with open('rugby_standings_SW.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(matches_json), f, ensure_ascii=False, indent=2)