import json
import os
import pymorphy2


class BooleanSearch:
    AND = "&"
    OR = "|"
    NOT = "~"
    OB = "("
    CB = ")"

    def __init__(self):
        self.path = os.getcwd()
        self.inverted_index_path = self.path  + '/inverted_index.json'
        self.inverted_index = self.read_inverted_index()
        self.morph = pymorphy2.MorphAnalyzer()

    def get_normal_form(self, word):
        morph = self.morph.parse(word)
        return morph[0].normal_form

    def read_inverted_index(self):
        with open(self.inverted_index_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        index = {}
        for key, value in data.items():
            index[key] = set(value)
        return index


    def searh(self, expression):
        search = expression.strip().split()

        result = self.OB
        for i in range(0, len(search)):
            el = search[i].lower()
            if el == self.OR:
                search[i] = el
                result += ").union("
            elif el == self.NOT:
                search[i] = el
                result += ").difference("
            elif el == self.AND:
              search[i] = el
              result += ").intersection("
            elif el == self.OB:
                search[i] = el
                result += self.OB
            elif el == self.CB:
                search[i] = el
                result += self.CB
            else:
                lemma = self.get_normal_form(el)
                search[i] = lemma
                if lemma in self.inverted_index.keys():
                    result += str(self.inverted_index[lemma])
                else:
                    result += "set()"
        result += self.CB

        return eval(result)


if __name__ == "__main__":
    boolean_search = BooleanSearch()
    """
    Примеры:
    союз & казань
    ( союз & выбор ) | автор
    ( казань | музыка ) & ~ педагог
    """

    while True:
        user_input = input("Введите поиск:\n")
        if user_input.lower() == 'exit':
            break

        try:
            result = boolean_search.searh(user_input)
            if len(result) == 0:
                print("Ничего не найдено")
            else:
                print(f"Результат поиска: {boolean_search.searh(user_input)}")
        except:
            print("Некорректный поисковой запрос. Попробуйте еще раз)")