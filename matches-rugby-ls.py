from playwright.sync_api import sync_playwright
from tqdm import tqdm
import pandas as pd
import json

def extract_team_names(teams: str):
    team_names = teams.split('vs')
    team_1 = team_names[0].strip()
    team_2 = team_names[1].strip()
    team_names = [convert_team_name(team_1), convert_team_name(team_2)]

    return team_names

def convert_team_name(team_name: str) -> str:
    team_mapping = {
        'Berliner Sport Verein': 'Berliner SV',
        'Berliner Rugby Club': 'Berliner RC',
        'FC Sankt Pauli': 'FC St. Pauli',
        'Deutscher Sportverein Hannover gegr. 1878 e.V.': 'Hannover 78',
        'Hamburger Rugby Club': 'Hamburger RC',
        'Rugby Club Leipzig': 'RC Leipzig',
        'Rugby Klub 03 Berlin': 'RK03 Berlin',
        'SC Germania List': 'Germania List',
        'Heidelberger Ruderklub': 'Heidelberger RK',
        'München Rugby Football Club': 'München RFC',
        'Rugby Club Luxemburg': 'RC Luxemburg',
        'Rugby Gesellschaft Heidelberg': 'RG Heidelberg',
        'Rugby Sport Verein Köln': 'RSV Köln',
        'Sport Club Frankfurt 1880': 'SC Frankfurt 1880',
        'Sport Club Neuenheim': 'SC Neuenheim',
        'TSV Handschuhsheim': 'TSV Handschuhsheim',
        'SC Germania List von 1900 e.V. Hannover 1.Herren': 'Germania List',
        'Berliner SV': 'Berliner SV',
        'Rugby Klub 03 Berlin e.V. I': 'RK03 Berlin',
        'Hamburger Rugby-Club von 1950 e.V. I': 'Hamburger RC',
        'FC St. Pauli von 1910 e.V.': 'FC St. Pauli',
        'Hamburger Rugby-Club von 1950 e.V.': 'Hamburger RC',
        'FC St.Pauli von 1910 e.V.I': 'FC St. Pauli',
        'FC St. Pauli von 1910 e.V. I': 'FC St. Pauli',
        'Berliner Rugby Club e.V. I': 'Berliner RC',
        'Rugby Club Leipzig e. V.': 'RC Leipzig',
        'Berliner Sport-Verein 1892 e.V.': 'Berliner SV',
        'RG Heidelberg 1898': 'RG Heidelberg',
        'SC Neuenheim 1902': 'SC Neuenheim',
        'München RFC': 'München RFC'
    }
    return team_mapping.get(team_name, team_name)

def scrape_rugby_matches(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        matches = []

        # Go to the page and wait for iframe to load
        page.goto(url)
        try:
            close_cookies = page.locator('.cmplz-close')
            if close_cookies.is_visible(timeout=3000):
                close_cookies.click()
        except:
            pass
        while True:
            current_table_page = page.locator('a.paginate_button.current').inner_text()
            rows = page.locator('tr.sp-row')
            count = rows.count()
            for i in tqdm(range(count)):
                date = rows.nth(i).locator('.data-date date').inner_text()
                teams = rows.nth(i).locator('.data-event').inner_text()
                team1, team2 = extract_team_names(teams)
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
                    'team1': team1,
                    'team2': team2,
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
    matches_df = scrape_rugby_matches("https://bits-rugby-ls.de/rugby-1-bundesliga-nord-ost")
    matches_json = matches_df.to_json(orient='records', date_format='iso')

    # Save to file
    with open('matches_NO.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(matches_json), f, ensure_ascii=False, indent=2)