# DBpedia Search Engine

This project is a simple web application that allows users to search for information on DBpedia using a search term. The application is built using Flask and RDFlib, and it caches search results to improve performance.

## Installation

To install the required dependencies, run the following commands:

```sh
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

pip install rdflib
pip install flask
pip install cachetools
pip install certifi

```

# To start the Flask application, run the following command:

```sh
python main.py

```
# Features
- Search for information on DBpedia using a search term.
- Display search results in a table format.
- Filter search results using a search filter.
- Display a thumbnail image if available.
- Print TTL file for the search term.
