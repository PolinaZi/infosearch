import math
import os
from typing import Dict, List
from nltk import word_tokenize
import json
import regex as re
import nltk

nltk.download('punkt')


class Searcher:

    def __init__(self):
        self.path = os.getcwd() + '/'
        self.tfidf_lemmas_folder_name = 'tfidf_lemmas'
        self.tfidf_lemmas_path = self.path.replace("task5", "task4") + self.tfidf_lemmas_folder_name + '/'
        self.tfid_file_name_prefix = 'tf_idf_'
        self.lemma_tokens_file_name = self.path.replace("task5", "task2") + 'lemma_tokens.txt'
        self.inverted_index_file_name = self.path.replace("task5", "task3") + 'inverted_index.json'
        self.pages_list = os.listdir(self.tfidf_lemmas_folder_name)
        self.pages_lemma_tfidf = self.get_pages_lemma_tfidf()
        self.lemma_tokens = self.get_lemma_tokens()
        self.inverted_index = self.get_inverted_index()
        self.pages_lengths = {page: self.calc_page_vector_length(self.pages_lemma_tfidf[page]) for page in
                              self.pages_list}

    def calc_page_vector_length(self, page_lemma_tfidf: Dict[str, float]):
        return math.sqrt(sum(i ** 2 for i in page_lemma_tfidf.values()))

    def get_pages_lemma_tfidf(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for file_name in os.listdir(self.tfidf_lemmas_folder_name):
            with open(self.tfidf_lemmas_path + file_name, encoding='utf-8') as tf_idf_file:
                lines = tf_idf_file.readlines()
                result[file_name] = {data[0]: float(data[2]) for data in
                                     [line.rstrip('\n').split(' ') for line in lines]}
        return result

    def get_lemma_tokens(self) -> Dict[str, str]:
        lemmas = {}
        with open(self.lemma_tokens_file_name, encoding='utf-8') as lemma_file:
            lines = lemma_file.readlines()
            for line in lines:
                line = line.rstrip('\n')
                words = line.split(' ')
                for word in words:
                    lemmas[word] = words[0]
        return lemmas

    def get_inverted_index(self):
        with open(self.inverted_index_file_name, encoding='utf-8') as file:
            json_index = file.readline()
            index = json.loads(json_index)
            return index

    def get_similarity_index(self, query_vector: List[str], doc_vector: Dict[str, float], doc_vector_len: int):
        return sum(doc_vector.get(token, 0) for token in query_vector) / len(query_vector) / doc_vector_len

    def get_pages_by_query(self, query: str):
        tokens = word_tokenize(query, language='russian')
        lemmas = [self.lemma_tokens[token] for token in tokens if token in self.lemma_tokens]
        pages_set = set()
        for lemma in lemmas:
            pages_set = pages_set.union(self.inverted_index.get(lemma, set()))

        pages_set_names = {self.tfid_file_name_prefix + page for page in pages_set}
        results = {page: self.get_similarity_index(lemmas, self.pages_lemma_tfidf[page + '.txt'],
                                                   self.pages_lengths[page + '.txt']) for page in pages_set_names}
        results = {re.findall(self.tfid_file_name_prefix + "([0-9]+)", key)[0]: value for key, value in results.items()}

        return dict(sorted(results.items(), key=lambda r: r[1], reverse=True))


if __name__ == '__main__':
    query_searcher = Searcher()
    while True:
        user_input = input("Введите поисковой запрос:\n")
        if user_input.lower() == 'exit':
            break

        try:
            print(query_searcher.get_pages_by_query(user_input))
        except Exception as e:
            print(f"Попробуйте еще раз! Произошло {e}")
