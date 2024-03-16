from flask import Flask, render_template, request
from searcher import query_searcher

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['input_value']
        result = query_searcher.get_pages_by_query(user_input)
        result_links = query_searcher.get_links_by_result(result)
        result_links = dict(list(result_links.items())[:10]) if result_links and len(result_links.items()) > 10 \
            else result_links
        return render_template('main.html', result=result_links, user_input=user_input)
    else:
        return render_template('main.html')


if __name__ == '__main__':
    app.run()
