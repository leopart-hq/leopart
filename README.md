# LEOPART
This is LEOPART, a fast search engine for electronic components in KicCad files on GitHub.

Leopart has 4 major components:
1. The Crawler (`crawler.py`) -- The crawler searches GitHub for KiCad files. The links to the pcb files and repository metadata is saved in a pickle file for parsing.
2. The Parser (`kicad_parser.py`) --  The parser downloads KiCad files from the pickle file produced by the crawler and extracts the components that are used in the project. The extracted information is saved to an SQLite database.
3. The Validator (`validator.py`) -- Builds a collection of known existing electronic components that is used to validate the components extracted by the parser.
4. The Search (`search.py`) and the Search Frontend (`app.py`) --  the search method finds fitting components from the built database and presents it on a webpage

# Installation Instructions
In order to use the project, please follow the developer manual in the `organizational` folder. This can be found [here](./organizational/developer_manual.md). 

# Usage Instructions
For usage instructions please refer to the [end user guide](./organizational/end_user_guide.md) in the `organizational` folder.

Note: for generating the HTML Documentation, you can execute the bash or bat files from the main directory.

# Info
This project was started as part of the 'High-tech entrepreneurship and new media' lab in the Winter Term 2019/20 at RWTH Aachen University.

# Members
- Lasse Mönch
- Avishek Chatterjee
- Mubasher Chaudhary
- Misha Yailoyan
- Marian Assenmacher