import os
import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.main_url = 'https://www.tatar-inform.ru/api/v1/news/getNews?widget_id=33&rubric={}&offset={}'
        self.rubric = '11'
        path = os.getcwd()
        self.pages_folder_name = path + '/pages'
        self.index_file_name = path + '/index.txt'
        os.mkdir(self.pages_folder_name)

    def find_links(self, count):
        links = []
        for i in range(0, count, 10):
            response = requests.get(self.main_url.format(self.rubric, str(i)))
            tree = BeautifulSoup(response.json()['data'], 'html.parser')

            for j in tree.select('.newsList__item'):
                link = j.select_one('a').attrs['href']
                links.append(link)

        return links

    def remove_unnecessary_tags(self, response):
        tree = BeautifulSoup(response, 'html.parser')
        unnecessary_tags = ['style', 'link', 'script']
        for tag in tree.find_all(unnecessary_tags):
            tag.extract()
        return str(tree)

    def download_pages(self, count: int = 100):
        links = list(set(self.find_links(count)))

        with open(self.index_file_name, 'w', encoding='utf-8') as f1:
            for i, link in enumerate(links):
                n = i + 1
                response = requests.get(link).text
                text = self.remove_unnecessary_tags(response)

                page_name = self.pages_folder_name + '/' + str(n) + '.html'
                with open(page_name, 'w', encoding='utf-8') as f2:
                    f2.write(text)

                f1.write(str(n) + ' ' + link + '\n')


if __name__ == '__main__':
    crawler = Crawler()
    crawler.download_pages()
