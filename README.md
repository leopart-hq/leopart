# LEOPART
KiCAD Search is a search engine for publicly available KiCAD pcb schematics on GitHub. It is currently being developed by a group of students at RWTH Aachen University as part of a lab course. We are currently not using GitHub as our main platform for development, but are using a GitLab instance that we currently can not make public, therefore this GitHub repo only serves to show our current state of development. When the lab course is finished, the development of this open source project will continue in this repository.

Play around with this at https://search-dev.aisler.net, where we are hosting the current development version on a server kindly provided by AISLER.

Even though this is not our main repository for development, you are very welcome to try the software and/or create issues, feature requests or pull requests!

1. The Crawler (`crawler.py`) -- The crawler runs over GitHub and searches for KiCad files. The links and repo info is saved for further processing.
2. The Parser (`kicad_parser.py`) --  The parser fetches the found files from the first step and extracts the components from it.
3. The Validator (`validator.py`) -- Builds a copy of parts and their information for validation of found components.
4. The Search (`search.py`) and the Search Frontend (`app.py`) --  the search finds fitting components from the built database and presents it on a webpage

# Setup Instructions
In order to set the project up, please follow the developer manual in the `organizational` folder. This can be found [here](./organizational/developer_manual.md). 

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
