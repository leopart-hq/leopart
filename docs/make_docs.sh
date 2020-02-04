export PARSER_CONFIG='./config/parser.config' && echo "Parser config saved"
export CRAWLER_CONFIG='./config/crawler.config' && echo "Crawler config saved"

sphinx-build -c docs docs/ docs/_build/ && echo "Finish"
