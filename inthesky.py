#!/usr/bin/env python3
import requests, re, datetime
from bs4 import BeautifulSoup
from pprint import pprint
from time import sleep


url = 'https://in-the-sky.org/newscal.php'
coordinates_url = 'https://recommendercomponent.azurewebsites.net/coordinates'

def get_fields(urls, params):
    for url in urls:
        fields = {}
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        fields['title'] = soup.select_one('p.widetitle').get_text()

        # Tags of interest are partially from dedicated elements and partially embedded in img icon text:
        fields['tags']  = [tag.get_text().strip() for tag in soup.select('span.event_tag')]
        fields['icons']  = [tag['title'].strip() for tag in soup.select('div.hidden-xs-down img')]
        fields['feed'] = soup.select_one('.condensed > i').get_text()
        fields['feed'] = re.sub(r'(\n| |\xa0)+', r' ', fields['feed'])
        
        fields['summary'] = '\n\n'.join(re.sub(r'(\n| |\xa0)+', r' ', p.get_text().strip()) 
                                        for p in soup.select('.newsbody > p')[:2])

        # We remove some whitespace from the body to make it look prettier when printed:
        fields['body']  = soup.select_one('div.newsbody').get_text().strip()
        fields['body']  = re.sub(r'(\n| |\xa0)+', r' ', fields['body'])

        yield fields


def main():
    
    coordinates = requests.get(coordinates_url, params={'limit': 10}).json()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    year, month, day = tomorrow.year, tomorrow.month, tomorrow.day

    for longitude, latitude in coordinates:

        params =  {
            'year': year,
            'month': month,
            'longitude': longitude,
            'latitude': latitude,
            'timezone': '+00:00',
            'maxdiff': 7 # Difficulty (7 is unobservable, so all events are retrieved here.)
        }

        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all event links for tomorrow:
        events = soup.select('.newscalday')[day - 1].findAll('a')
        urls = [a['href'] for a in events]

        for fields in get_fields(urls, params):
            # Post content to API):

            # requests.post('http://127.0.0.1:8000', json=content)
            sleep(2)
            print(fields)
            exit()
            # os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()