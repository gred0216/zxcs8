from zxcs8 import *
import logging
from sorter import *


def main():
    '''
    The main() do three tasks:
    1. Get every category and create shelf
    2. Get every book of the shelf
    3. Save the shelf and ranking result
    '''
    logger = set_log()
    logger.info('scrawler start')
    tags, sort = get_category()

    os.makedirs('./tags/', exist_ok=True)
    os.makedirs('./sort/', exist_ok=True)
    for category in tags, sort:
        for name, link in category.items():
            path = 'tags'
            tmp_shelf = create_shelf(name, link)
            save_score(*(sort_by_overall(tmp_shelf) + (path,)))

            shelf_json = tmp_shelf.to_json()
            with open('./%s/%s.txt' % (path,name), 'w', encoding='UTF-8') as f:
                f.write(shelf_json)
        path = 'sort'

    logger.info('scrawler stop')
    logging.shutdown()


def set_log():
    '''
    Return logger.
    '''
    logger = logging.getLogger('zxcs8')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    # filehandler write to scrawler.log under current working directory
    fh = logging.FileHandler('scrawler.log', encoding='UTF-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    # streamhandler only print out log warning or above
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def get_category():
    '''
    Return all categories and their links in tag and sort
    '''
    r = requests.get('http://www.zxcs8.com/map.html')
    r.encoding = 'UTF-8'
    if r.ok:
        soup = BeautifulSoup(r.text)
    tag_a = soup.find(id='tags').find_all('a')
    tags = {}
    for i in tag_a:
        text = re.match('(.*)\(', i.text)[1]
        href = i.get('href')
        tags[text] = href

    sort_a = soup.find(id='sort').find_all('a')
    sort = {}
    for i in sort_a:
        if i.img:
            continue
        text = re.match('(.*)\(', i.text)[1]
        href = i.get('href')
        sort[text] = href

    return tags, sort


def create_shelf(shelf_name, shelf_link):
    temp_shelf = Shelf(shelf_link, shelf_name)
    temp_shelf.get_books()
    return temp_shelf


if __name__ == '__main__':
    main()
