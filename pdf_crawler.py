"""
crawler for pdf slides download
"""

import os
import requests
import argparse
from bs4 import BeautifulSoup
from multiprocessing import Pool
from urllib import parse
from functools import partial
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Parameters for PDF crawler')
parser.add_argument('--folder', default='slides', type=str, help='folder name')
parser.add_argument('--pool', default=8, type=int, help='pool number')
parser.add_argument('--mode', default='keyword', type=str, help='filter mode, keyword/ruleout')
parser.add_argument('--record', default=True, type=bool, help='whether to write links to files')
args = parser.parse_args()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/32.0.1700.76 Safari/537.36'
}


def download_file(url, folder_name):
    local_filename = url.split('/')[-1]
    save_path = os.path.join(folder_name, local_filename)
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            # filter out keep-alive new chunks
            if chunk:
                f.write(chunk)
                f.flush()
    return save_path


# root_link = r"http://www.cs.princeton.edu/~wayne/kleinberg-tardos/"
# root_link = r"http://www.cs.cmu.edu/~epxing/Class/10708-14/lecture.html"
# root_link = r'https://www.cs.cmu.edu/~epxing/Class/10708-20/lectures.html'


def filter(path, keywords):
    """
    input: input path, keywords (a list)
    output: True/False 
    """
    if not keywords:
        return True
    if isinstance(keywords, str):
        keywords = [keywords] 
    if isinstance(keywords, tuple):
        keywords = list(keywords)        
    for keyword in keywords:
        if keyword in path:
            return True
    else:
        return False


def main():
    # root_link = input('input link here: ')
    root_link = r'https://www.cs.cmu.edu/~epxing/Class/10708-20/lectures.html'
    root_link = root_link.lstrip()
    root_link = root_link.rstrip()
    folder_name = input('folder name: (default: slides) ')
    if folder_name: 
        if not os.path.exists(folder_name):
            path = "./" + folder_name
            os.makedirs(path)
    else:
        folder_name = args.folder
        
    filter_word = 1
    filter_list = []
    while filter_word:
        filter_word = input('input filter word, terminated if no input: ')
        if filter_word:
            filter_list.append(filter_word)
        
    print('this is the filter words you choose')
    for word in filter_list:
        print(word)
        
    req = requests.get(root_link, headers=headers)
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, "lxml")
        new_links = []
        filter_outs = []
        
        for link in soup.find_all('a'):
            available_link = link.get('href')
            if available_link.endswith(".pdf"):
                new_link = parse.urljoin(root_link, available_link, allow_fragments=True)
                if filter(new_link, filter_list):
                    new_links.append(new_link)
                    
                else:
                    filter_outs.append(new_link)
                    continue
        
        for new_link in new_links:
            print("New link: {}".format(new_link))
        print('{} files int total.\n'.format(len(new_links)))

        if args.record is True:
            with open(os.path.join(folder_name, 'filter_out.txt'), 'w') as f:
                for filter_out in filter_outs:
                    f.write(filter_out + '\n')
            print('write to filter_out.txt')
        else:
            for filter_out in filter_outs:
                print('**filter out {}'.format(filter_out))

        # pool = Pool(8)
        _func = partial(download_file, folder_name=folder_name)

        pool_num = args.pool
        with Pool(pool_num) as pool:
            r = list(tqdm(pool.map(_func, new_links), total=len(new_links)))
            pool.close()
            pool.join()

        print("all download finished\n")


if __name__ == '__main__':
    main()