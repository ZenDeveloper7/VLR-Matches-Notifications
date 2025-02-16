import functions_framework
import requests
from bs4 import BeautifulSoup
import json

@functions_framework.http
def get_vlr_matches(request):
    all_matches = []
    current_page = 1

    # URL of the first page to scrape
    url = 'https://www.vlr.gg/matches'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_pages = get_total_pages(soup)
    all_matches.extend(scrape_page(url))

    # Loop through all pages
    for current_page in range(1, total_pages+1):
        print("Scraping " + url)
        all_matches.extend(scrape_page(url))
        url = 'https://www.vlr.gg/matches?page=' + str(current_page + 1)

    # Convert the matches list to JSON
    matches_json = json.dumps(all_matches, indent=4)

    return matches_json

def scrape_page(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    matches_list = []
    current_date = ""

    # Find all match details
    date_labels = soup.find_all('div', class_='wf-label mod-large')
    for date_label in date_labels:
        current_date = date_label.get_text(strip=True)

        match_container = date_label.find_next_sibling('div')
        matches = match_container.find_all('a', class_='match-item')
        
        for match in matches:
            match_time = match.find('div', class_='match-item-time').get_text(strip=True)
            match_status = match.find('div', class_='ml-status').get_text(strip=True)
            match_event = match.find('div', class_='match-item-event').get_text(strip=True)
            teams = match.find_all('div', class_='match-item-vs-team-name')
            team1 = teams[0].get_text(strip=True)
            team2 = teams[1].get_text(strip=True)
            href = match['href']
            
            match_details = {
                'date': current_date.replace("Today", ""),
                'time': match_time,
                'status': match_status,
                'event': match_event,
                'team1': team1,
                'team2': team2,
                'href': href
            }
            
            matches_list.append(match_details)
    
    return matches_list

def get_total_pages(soup):
    page_numbers = soup.find_all('a', class_='btn mod-page')
    if page_numbers:
        return int(page_numbers[-1].get_text(strip=True))
    return 1