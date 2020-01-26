from flask import Flask
from flask import request
from flask import render_template
from sassutils import builder
from search import search
import json

app = Flask(__name__)
compiled = builder.build_directory(
    sass_path="static/scss",
    css_path="static/css",
    strip_extension=False
)
if app.debug or app.env == "development":
    print("Compiled scss:", compiled)


@app.route('/', methods=['GET'])
def index():
    """
    Index Page

    :return: rendered Page
    """
    query = request.args.get('q')

    print(query)

    if query is not None:
        return search_component(query)
    else:
        return render_template('index.html')


def search_component(query):
    """
    Index page w/ search results

    :return: rendered Page
    """
    # text = request.form['search_text']
    text = query

    # !!!!!!
    # WARNING: no text sanitation done here. Expected to be done in search!
    # !!!!!!

    search_results = search(text)
    json_results = json.loads(search_results)

    return render_template('index.html', searchResult=json_results, searchComponent=text)


if __name__ == "__main__":
    app.run(debug=True)
