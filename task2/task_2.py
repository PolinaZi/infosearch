import nltk
import string
import re
import pymorphy2
from os import listdir
import os
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


class Tokenlemmatizer:
    def __init__(self):
        self.path = os.getcwd()
        self.pages_folder_name = self.path.replace("task2", "task1") + '/pages'
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('russian'))
        self.morph = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = dict()

    def save_tokens(self):
        with open(self.path + '/tokens.txt', 'w') as tokens_file:
            for token in self.tokens:
                tokens_file.write(token + '\n')

    def save_lemma_tokens(self):
        with open(self.path + '/lemma_tokens.txt', 'w') as lemmas_file:
            for lemma, tokens in self.lemmas.items():
                line = lemma + ' '
                for token in tokens:
                    line += token + ' '
                line += '\n'
                lemmas_file.write(line)

    def is_correct_token(self, token):
        has_punctuation = True if any(x in string.punctuation for x in token) else False
        is_stop_word = bool(token.lower() in self.stop_words)
        is_number = bool(re.compile(r'^[0-9]+$').match(token))
        is_russian = bool(re.compile(r'^[а-яА-Я]{2,}$').match(token))
        is_good_word = True if self.morph.parse(token)[0].score >= 0.5 else False
        return not has_punctuation and not is_stop_word and not is_number and is_russian and is_good_word

    def get_tokens(self):
        for page_name in listdir(self.pages_folder_name):
            with open(self.pages_folder_name + '/' + page_name, 'r', encoding='utf-8') as html:
                text = BeautifulSoup(html, features='html.parser').get_text().lower()
                tokens = wordpunct_tokenize(text)
                self.tokens = self.tokens | set(filter(self.is_correct_token, tokens))
        self.save_tokens()

    def group_tokens_by_lemmas(self):
        for token in self.tokens:
            parsed_token = self.morph.parse(token)[0]
            normal_form = parsed_token.normal_form if parsed_token.normalized.is_known else token.lower()
            if normal_form not in self.lemmas:
                self.lemmas[normal_form] = []
            self.lemmas[normal_form].append(token)
        self.save_lemma_tokens()


if __name__ == '__main__':
    tokenlemmatizer = Tokenlemmatizer()
    tokenlemmatizer.get_tokens()
    tokenlemmatizer.group_tokens_by_lemmas()
