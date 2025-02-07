import time
import math
from playwright.sync_api import sync_playwright
import pandas as pd
import json


def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        matches = []

        # Go to the page and wait for content to load
        page.goto(url)
        try:
            page.wait_for_selector('.s50-cookie-banner__button-outlined button', timeout=3000)
            close_cookies = page.locator('.s50-cookie-banner__button-outlined button')
            if close_cookies.is_visible(timeout=3000):
                close_cookies.click()
        except:
            pass

        # Wait for content and scroll
        page.wait_for_selector('.MuiTypography-h3')

        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

        # Get all text elements that could be either Spieltag headers or scores
        elements = page.locator('.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation1.MuiCard-root.mui-1hm4dm').all()

        for i, element in enumerate(elements):
            home_team = element.locator('p.MuiTypography-root.MuiTypography-body2 b').first.inner_text().split(" (")[0].rsplit(" 1", 1)[0]
            away_team = element.locator('p.MuiTypography-root.MuiTypography-body2.mui-nqo5y4 b').nth(1).inner_text().split(" (")[0].rsplit(" 1", 1)[0]
            date = element.locator('p.MuiTypography-root.MuiTypography-body2').nth(1).inner_text()
            standings_or_time = element.locator('h3.MuiTypography-root.MuiTypography-h3.mui-1df5zv').inner_text()
            gameday = math.ceil((i+1)/4)

            if " : " in standings_or_time:
                score = standings_or_time.split(" : ")
                home_score = score[0]
                away_score = score[1]
                game_time = False
            else:
                home_score = None
                away_score = None
                game_time = standings_or_time

            match_data = {
                'gameday': gameday,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'date': date,
                'game_time': game_time,
            }

            matches.append(match_data)
        browser.close()
        return pd.DataFrame(matches)


if __name__ == "__main__":
    matches_df = scrape_rugby_matches("https://www.rugbydeutschland.org/spiele-81794v4/leagues/9604/seasons/216")
    print(matches_df)  # Print to verify the output
    matches_json = matches_df.to_json(orient='records', date_format='iso')

    # Save to file
    with open('rugby_scores_NO.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(matches_json), f, ensure_ascii=False, indent=2)