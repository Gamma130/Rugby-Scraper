from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd


def scrape_rugby_matches():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to the page and wait for iframe to load
        page.goto("https://nrv-rugby.de/ergebnisse-bundesliga/")

        # Debug frame information
        frames = page.frames
        print(f"Found {len(frames)} frames")
        for i, frame in enumerate(frames):
            print(f"Frame {i}: URL = {frame.url}")

        try:
            # Wait for the third frame to load (index 2) since that's where our content is
            frame = frames[2]

            # Wait for content inside frame
            frame.wait_for_selector("table.box_content", timeout=60000)

            # Get content from frame
            content = frame.content()
            soup = BeautifulSoup(content, 'html.parser')

            matches = []
            # Find all match rows (excluding mobile rows)
            match_rows = soup.find_all('tr', class_=lambda x: x and 'match_date_' in x and 'show_mobile' not in x)

            print(f"Found {len(match_rows)} matches")

            for row in match_rows:
                try:
                    # Get date and time
                    date_div = row.find('span', class_='match_date')
                    time_div = row.find('span', class_='match_time')
                    date = date_div.text.strip() if date_div else None
                    time = time_div.text.strip() if time_div else None

                    # Get venue
                    venue_cell = row.find('td', class_=lambda x: x and 'cell_2' in x and 'show_notmobile' in x)
                    venue = venue_cell.text.strip() if venue_cell else None

                    # Get teams
                    team1_cell = row.find('td', class_='match_team1')
                    team2_cell = row.find('td', class_='match_team2')

                    team1_name = team1_cell.find('div', class_='team_name_inner').text.strip() if team1_cell else None
                    team2_name = team2_cell.find('div', class_='team_name_inner').text.strip() if team2_cell else None

                    # Get team ranks
                    team1_rank = team1_cell.find('span', class_='teamrank_left').text.strip() if team1_cell else None
                    team2_rank = team2_cell.find('span', class_='teamrank_right').text.strip() if team2_cell else None

                    # Get score
                    score_div = row.find('div', class_='dates_match_result')
                    if score_div:
                        score1 = score_div.find('span', {'class': ['result_gt', 'result_lt', 'result_eq']})
                        score2 = score_div.find_all('span')[-1]
                        score = f"{score1.text.strip()}-{score2.text.strip()}" if score1 and score2 else None
                    else:
                        score = None

                    # Get match points
                    points_div = row.find('div', class_='dates_match_points')
                    points = points_div.text.strip() if points_div else None

                    # Get match status
                    match_winner = row.find('div', class_='match_winner')
                    status = "Completed" if match_winner else "Scheduled"

                    matches.append({
                        'Date': date,
                        'Time': time,
                        'Venue': venue,
                        'Home_Team': team1_name,
                        'Home_Rank': team1_rank,
                        'Away_Team': team2_name,
                        'Away_Rank': team2_rank,
                        'Score': score,
                        'Match_Points': points,
                        'Status': status
                    })

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

        except Exception as e:
            print(f"Major error: {e}")
            return None

        finally:
            browser.close()

        # Create DataFrame and clean up
        df = pd.DataFrame(matches)

        # Clean up rank strings
        if 'Home_Rank' in df.columns:
            df['Home_Rank'] = df['Home_Rank'].str.replace('Platz ', '')
        if 'Away_Rank' in df.columns:
            df['Away_Rank'] = df['Away_Rank'].str.replace('Platz ', '')

        return df


if __name__ == "__main__":
    # Run the scraper
    matches_df = scrape_rugby_matches()

    if matches_df is not None:
        # Display the results
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print("\nExtracted matches:")
        print(matches_df)

        # Save to CSV
        matches_df.to_csv('rugby_matches-NO.csv', index=False)
        print("\nData saved to rugby_matches-NO.csv")
    else:
        print("Failed to extract matches data")