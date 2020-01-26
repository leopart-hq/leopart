# LEOPART
This is LEOPART, the fast easy search engine for electronic components in KicCad files on GitHub.

Gustav has 4 major components:
1. The Crawler (`crawler.py`) -- The crawler runs over GitHub and searches for KiCad files. The links and repo info is saved for further processing.
2. The Parser (`kicad_parser.py`) --  The parser fetches the found files from the first step and extracts the components from it.
3. The Validator (`validator.py`) -- Builds a copy of parts and their information for validation of found components.
4. The Search (`search.py`) and the Search Frontend (`app.py`) --  the search finds fitting components from the built database and presents it on a webpage

# Build Instructions
In order to build the project, please follow the developer manual in the `organizational` folder. This can be found [here](./organizational/developer_manual.md). 

# Usage Instructions
For usage instructions please refer to the [end user guide](./organizational/end_user_guide.md) in the `organizational` folder.

# Info
This project was done as part of the 'High-tech entrepreneurship and new media' lab in the Winter Term 2019/20 at RWTH Aachen University.

# Members
- Lasse Mönch
- Avishek Chatterjee
- Mubasher Chaudhary
- Misha Yailoyan
- Marian Assenmacher