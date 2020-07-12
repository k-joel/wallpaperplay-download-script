from bs4 import BeautifulSoup, SoupStrainer
from mimetypes import guess_extension
from tqdm import tqdm
import httplib2
import requests
import sys
import re
import os


def download(file_dir, url):
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get('Content-Length', 0))
    # get the file name
    file_type = response.headers.get('Content-Type').split(';')[0]
    file_name = os.path.join(file_dir, url.split(
        '/')[-1] + guess_extension(file_type))
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(
        1024), f'Downloading \'{file_name}\'', total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(file_name, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def main(url):
    # validate and match directory
    r = re.compile(r'https://wallpaperplay.com/board/(.+)')
    m = re.match(r, url)
    if m == None:
        print("Error! Invalid url")
        return
    file_dir = m.group(1)
    # parse url and retrieve links
    print(f'Searching for images at \'{url}\'...')
    http = httplib2.Http()
    _, response = http.request(url)
    soup = BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a'))
    links = [link['data-download']
             for link in soup if link.has_attr('data-download')]
    print(f'Done! Found {len(links)} files.')
    # create directory if it doesn't exist
    if not os.path.isdir(file_dir):
        print(f'Creating directory: {file_dir}')
        os.makedirs(file_dir)
    else:
        opt = input(
            f'Warning: directory \'{file_dir}\' already exists. This operation will overwrite existing files. Proceed? (y/n): ').lower()
        while opt != 'y':
            if opt == 'n':
                print('Aborting...')
                return
            opt = input('Invalid input. Proceed? (y/n): ').lower()
    # download all links
    print('Downloading images...')
    for link in links:
        download(file_dir, link)
    print('Finished!')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(r'Usage: .\python wpp.py https://wallpaperplay.com/board/4k-hd-wallpapers')
        print('Downloads all images from the specified url.')
    else:
        main(sys.argv[1])
