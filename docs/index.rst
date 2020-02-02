Welcome to Leopart's developer documentation!
===============================================
Leopart consists of 4 main components: A Crawler to find GitHub repositories containing KiCad files, a parser to parse
these KiCad files and extract the parts used in them, a validator to see if these parts (which are freetext in KiCad
files) are actual parts that can be bought, and a small flask app that allows users to search for projects containing
specific components. Read

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   developer_manual.md
   crawler.rst
   parser.rst
   validator.rst



Components
==================

* :ref:`Crawler <crawler>`
* :ref:`Parser <parser>`
* :ref:`Validator <validator>`
