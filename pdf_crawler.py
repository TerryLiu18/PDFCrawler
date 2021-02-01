"""
crawler for pdf slides download
"""

import os
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from urllib import parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/32.0.1700.76 Safari/537.36'
}


def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            # filter out keep-alive new chunks
            if chunk:
                f.write(chunk)
                f.flush()
    return local_filename


# root_link = r"http://www.cs.princeton.edu/~wayne/kleinberg-tardos/"
root_link = r"http://www.cs.cmu.edu/~epxing/Class/10708-14/lecture.html"


def main():
    req = requests.get(root_link, headers=headers)
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, "lxml")
        new_links = []

        for link in soup.find_all('a'):
            available_link = link.get('href')
            if available_link.endswith(".pdf"):
                new_link = parse.urljoin(root_link, available_link, allow_fragments=True)
                print("New link: {}".format(new_link))
                new_links.append(new_link)

        # links = [root_link + l.get('href') for l in links if l.get('href')]
        # pdf_links = [l for l in links if l.endswith(".pdf")]

        pool = Pool(8)
        results = pool.map(download_file, new_links)
        print("all download finished\n")


if __name__ == '__main__':
    main()