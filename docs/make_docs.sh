export PARSER_CONFIG='./config/default_parser.config' && echo "Parser config saved"
export CRAWLER_CONFIG='./config/default_crawler.config' && echo "Crawler config saved"

sphinx-build -c docs docs/ docs/_build/ && echo "Finish"
