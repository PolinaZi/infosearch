import re
import pymorphy2
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
import os
import json


class InvertedIndex:
    def __init__(self):
        self.path = os.getcwd()
        self.pages_folder_name = self.path.replace("task3", "task1")  + '/pages'
        self.lemmas_file_name = self.path.replace("task3", "task2")  + '/lemma_tokens.txt'
        self.inverted_index_file_name = self.path + '/inverted_index.json'
        self.morph = pymorphy2.MorphAnalyzer()
        self.lemmas = dict()
        self.index = dict()

    def read_lemmas(self):
        with open(self.lemmas_file_name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                words = re.split(' ', line)
                key = words[0]
                self.lemmas[key] = []
                for i in range(1, len(words) - 1):
                    self.lemmas[key].append(words[i])

    def get_index(self):
        for file_name in listdir(self.pages_folder_name):
            with open(self.pages_folder_name + '/' + file_name, 'r', encoding='utf-8') as file:
                text = BeautifulSoup(file, features='html.parser').get_text()
                list_of_words = wordpunct_tokenize(text)
                words = set()
                for word in list_of_words:
                    parsed_word = self.morph.parse(word)[0]
                    lemma = parsed_word.normal_form if parsed_word.normalized.is_known else word.lower()
                    if lemma in self.lemmas.keys() and lemma not in words:
                        words.add(lemma)
                        word_forms = self.lemmas[lemma]
                        if lemma not in self.index.keys():
                            self.index[lemma] = []
                        self.index[lemma].append(re.search('\\d+', file_name)[0])

    def write_index(self):
        json_inverted_index = json.dumps(self.index, ensure_ascii=False)
        with open(self.inverted_index_file_name, 'w+', encoding='utf-8') as index_file:
            index_file.write(json_inverted_index)

    def create_index_file(self):
        self.read_lemmas()
        self.get_index()
        self.write_index()


if __name__ == '__main__':
    inverted_index = InvertedIndex()
    inverted_index.create_index_file()