import os
import string
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from bs4 import BeautifulSoup as bs
import pymorphy2
import re


class TFIDFCounter:
    def __init__(self):
        self.path = os.getcwd()
        self.output_tokens_folder_name = self.path + '/tfidf_tokens'
        self.output_lemmas_folder_name = self.path + '/tfidf_lemmas'
        self.pages_folder_name = self.path.replace("task4", "task1") + '/pages'
        self.tokens_file_name = self.path.replace("task4", "task2") + '/tokens.txt'
        self.lemmas_file_name = self.path.replace("task4", "task2") + '/lemma_tokens.txt'
        self.morph = pymorphy2.MorphAnalyzer()
        nltk.download('stopwords')
        self.stop_words = stopwords.words('russian')

    def get_lemmas_documents(self, pages):
        lemmas_documents = []
        for page in pages:
            tokens = page.split()
            parsed_tokens = [self.morph.parse(token)[0] for token in tokens]
            lemmas = []
            for parsed_token, token in zip(parsed_tokens, tokens):
                lemmas.append(parsed_token.normal_form if parsed_token.normalized.is_known else token)

            lemmas_documents.append(' '.join(lemmas))
        return lemmas_documents

    def is_correct_token(self, token):
        has_punctuation = True if any(x in string.punctuation for x in token) else False
        is_stop_word = bool(token.lower() in self.stop_words)
        is_number = bool(re.compile(r'^[0-9]+$').match(token))
        is_russian = bool(re.compile(r'^[а-яА-Я]{2,}$').match(token))
        is_good_word = True if self.morph.parse(token)[0].score >= 0.5 else False
        return not has_punctuation and not is_stop_word and not is_number and is_russian and is_good_word

    def get_pages(self):
        pages = []
        for i in range(1, 101):
            filename = f'{i}.html'
            with open(os.path.join(self.pages_folder_name, filename), 'r', encoding='utf-8') as html:
                text = bs(html, features='html.parser').get_text().lower()
                tokens = wordpunct_tokenize(text)
                tokens = filter(self.is_correct_token, tokens)
                pages.append(' '.join(tokens))
        return pages

    def read_tokens(self):
        with open(self.tokens_file_name, 'r', encoding='utf-8') as f:
            return [token.strip() for token in f.readlines()]

    def read_lemmas(self):
        lemmas = []
        with open(self.lemmas_file_name, 'r', encoding='utf-8') as file:
            lemmas = []
            for line in file:
                lemmas.append(line.split()[0])
        return lemmas

    def calc_tf_idf_for_tokens(self, tokens, pages):
        tfidf_vectorizer = TfidfVectorizer(vocabulary=tokens, stop_words=self.stop_words, lowercase=True)
        tfidf_matrix = tfidf_vectorizer.fit_transform(pages)

        for i, tfidf_row in enumerate(tfidf_matrix):
            tfidf_values = tfidf_row.toarray()[0]
            output_filename = os.path.join(self.output_tokens_folder_name, f'tf_idf_{i + 1}.txt')
            with open(output_filename, 'w', encoding='utf-8') as f:
                for token, tfidf_value in zip(tokens, tfidf_values):
                    if tfidf_value != 0:
                        f.write(f"{token} {tfidf_vectorizer.idf_[tfidf_vectorizer.vocabulary_[token]]} {tfidf_value}\n")

    def calc_tf_idf_for_lemmas(self, lemmas, lemmas_documents):
        tfidf_vectorizer_lemmas = TfidfVectorizer(vocabulary=lemmas, stop_words=self.stop_words, lowercase=True)
        tfidf_matrix_lemmas = tfidf_vectorizer_lemmas.fit_transform(lemmas_documents)

        for i, tfidf_row in enumerate(tfidf_matrix_lemmas):
            tfidf_values = tfidf_row.toarray()[0]
            output_filename = os.path.join(self.output_lemmas_folder_name, f'tf_idf_{i + 1}.txt')
            with open(output_filename, 'w', encoding='utf-8') as f:
                for lemma, tfidf_value in zip(lemmas, tfidf_values):
                    if tfidf_value != 0:
                        f.write(
                            f"{lemma} {tfidf_vectorizer_lemmas.idf_[tfidf_vectorizer_lemmas.vocabulary_[lemma]]} {tfidf_value}\n")

    def calculate_tf_idf(self):
        pages = self.get_pages()
        tokens = self.read_tokens()
        lemmas = self.read_lemmas()

        self.calc_tf_idf_for_tokens(tokens, pages)

        lemmas_documents = self.get_lemmas_documents(pages)
        self.calc_tf_idf_for_lemmas(lemmas, lemmas_documents)


if __name__ == '__main__':
    counter = TFIDFCounter()
    counter.calculate_tf_idf()
