import ssl
import certifi
import urllib.request
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from cachetools import cached, TTLCache

# Create a custom HTTPS opener that uses the certifi certificate bundle
ssl_context = ssl.create_default_context(cafile=certifi.where())
https_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(https_handler)
urllib.request.install_opener(opener)

# Cache for search results
search_cache = TTLCache(maxsize=100, ttl=300)  # 5 minute cache

@cached(search_cache)
def search(searchTerm):
    store = SPARQLStore("https://dbpedia.org/sparql")
    g = Graph(store=store)
    g.open("https://dbpedia.org/sparql")

    query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX dbp: <http://dbpedia.org/property/>

        SELECT DISTINCT ?property ?value ?thumbnail
        WHERE {{
            res:{searchTerm} ?property ?value .
            OPTIONAL {{ res:{searchTerm} dbo:thumbnail ?thumbnail }}
            FILTER (lang(?value) = 'en' || !isLiteral(?value))
            FILTER (?property NOT IN (rdf:type, dbp:align, owl:sameAs, dbp:wikt, dbp:s, dbp:b))
        }}
        ORDER BY ?property
    """

    results = g.query(query)

    resultList = []
    for row in results:
        resultList.append({
            "property": str(row["property"]).split("/")[-1],
            "value": str(row["value"]),
            "thumbnail": str(row["thumbnail"]) if row["thumbnail"] else None
        })

    return resultList

def formatResults(results):
    formattedResults = {}
    thumbnail = None
    for result in results:
        propertyName = result["property"]
        propertyValue = result["value"]

        if result["thumbnail"]:
            thumbnail = result["thumbnail"]

        if propertyValue.startswith(("http://", "https://")):
            propertyValue = f'<a href="{propertyValue}" target="_blank">{propertyValue.split("/")[-1]}</a>'

        formattedResults.setdefault(propertyName, []).append(propertyValue)

    return formattedResults, thumbnail

# Cache for graph results
graph_cache = TTLCache(maxsize=100, ttl=300)  # 5 minute cache

@cached(graph_cache)
def get_graph(search_term):
    g = Graph()
    g.parse('http://dbpedia.org/resource/{0}'.format(search_term), format='n3')

    g.query(f'''
      SELECT DISTINCT ?property ?value
        WHERE {{
          dbr:{search_term} ?property ?value .
          FILTER (lang(?label) = 'en' || !isLiteral(?value))
      }}
    ''')

    return g

def printTtlResults(search_term):
    return get_graph(search_term)