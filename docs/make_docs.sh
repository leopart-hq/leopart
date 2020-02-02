export PARSER_CONFIG='./config/example_parser.config' && echo "Parser config saved"
export CRAWLER_CONFIG='./config/example_crawler.config' && echo "Crawler config saved"

sphinx-build -c docs docs/ docs/_build/ && echo "Finish"
