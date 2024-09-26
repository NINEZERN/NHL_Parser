import requests
from bs4 import BeautifulSoup
import re
import json

URL = "https://www.nhl.com/scores/htmlreports/20232024/TH020692.HTM"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
}


def extract_player_info(soup):
    player_info = {}

    def extract_player_heading():
        player_heading = soup.find('td', class_='playerHeading')
        if player_heading:
            player_heading_text = player_heading.get_text(strip=True)
            match = re.match(r'(\d+)\s+([A-Z\s,]+)', player_heading_text)
            if match:
                return {
                    'player_number': int(match.group(1)),
                    'name': match.group(2).strip()
                }
        return {}

    def extract_shifts():
        shifts = []
        shifts_rows = soup.find_all('tr', class_=['oddColor', 'evenColor'])
        for row in shifts_rows:
            shift_number_text = row.find('td', class_='lborder').get_text(strip=True)
            if shift_number_text.isdigit():
                shift_data = {
                    'shift_number': int(shift_number_text),
                    'period': row.find_all('td', class_='lborder')[1].get_text(strip=True),
                    'start_of_shift': row.find_all('td', class_='lborder')[2].get_text(strip=True),
                    'end_of_shift': row.find_all('td', class_='lborder')[3].get_text(strip=True),
                    'duration': row.find_all('td', class_='lborder')[4].get_text(strip=True),
                    'event': row.find_all('td', class_='lborder')[5].get_text(strip=True) if row.find_all('td', class_='lborder')[5] else None
                }
                shifts.append(shift_data)
        return shifts

    def extract_periods():
        periods = []
        periods_table = soup.find('table', {'cellpadding': 0})
        if periods_table:
            periods_rows = periods_table.find_all('tr')
            headers = [header.get_text(strip=True).replace('\u00a0', '_') for header in periods_rows[0].find_all('td')]
            for row in periods_rows[1:]:
                period_data = {headers[i]: row.find_all('td')[i].get_text(strip=True).replace('\u00a0', ' ') for i in range(min(len(headers), len(row.find_all('td'))))}
                periods.append(period_data)
        return periods

    player_info['player_heading'] = extract_player_heading()
    player_info['shifts'] = extract_shifts()
    player_info['periods'] = extract_periods()

    return player_info


def get_html_data() -> list:
    """Will return a list of html data of players. First element is gonna be a header"""

    r = requests.get(URL, headers=HEADERS)

    input_string = r.text
    delimiter = '<td align="center" valign="top" class="playerHeading + border'

    # Escape special characters in the delimiter
    escaped_delimiter = re.escape(delimiter)

    # Create a regular expression with positive lookahead
    regex = f'(?={escaped_delimiter})'

    # Split the string using the regular expression
    html_data = re.split(regex, input_string)
    return html_data


def main():
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')

    html_data = get_html_data()
    header = html_data[0]
    players = html_data[1:]


    for n, player in enumerate(players):
        soup = BeautifulSoup(player, 'html.parser')
        result = extract_player_info(soup)

        # Write players info to json files
        with open(f'player-{n + 1}.json', 'w') as json_file:
            json.dump(result, json_file, indent=4)


if __name__ == "__main__":
    main()