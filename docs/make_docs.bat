SET PARSER_CONFIG=.\config\example_parser.config
SET CRAWLER_CONFIG=.\config\example_crawler.config
sphinx-build -c docs docs docs\_build && echo "Finish"
