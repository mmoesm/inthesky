#!/usr/bin/env python3
import asyncio, requests, re, os
from bs4 import BeautifulSoup
from pprint import pprint

params =  {
    'month': 10,
    'year': 2021,
    'maxdiff': 7, # Difficulty (7 is unobservable, so all events are retrieved here.)
    'latitude': 57.05,
    'longitude': 9.92,
    'timezone': '+02:00'
}

url = 'https://in-the-sky.org/newscal.php'


async def get_fields(urls, params):
    for url in urls:
        content = {}
        response = requests.get(urls[url], params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        content['title'] = soup.select_one('p.widetitle').get_text()

        # Tags of interest are partially from dedicated elements and partially embedded in img icon text:
        content['tags']  = [tag.get_text().strip() for tag in soup.select('span.event_tag')]
        content['tags'] += [tag['title'].strip() for tag in soup.select('div.hidden-xs-down img')]

        # We remove some whitespace from the body to make it look prettier when printed:
        content['body']  = soup.select_one('div.newsbody').get_text().strip()
        content['body']  = re.sub(r'(\n| )+', r' ', content['body'])
        yield content


async def main():
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get all links from the calendar:
    events = soup.select('.newscalitem > a')
    titles = {a['title']: a['href'] for a in events}

    async for content in get_fields(titles, params):
        # Post content to API):
        # requests.post('http://127.0.0.1:8000', json=content)
        await asyncio.sleep(2)
        pprint(content)
        # os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())