import os
from flask import Flask, request, render_template_string
from query import *
import html

app = Flask(__name__)

styles = """
<style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    form { margin-bottom: 20px; }
    label { font-weight: bold; }
    input[type="text"] { width: 300px; padding: 5px; margin-right: 10px; }
    button { padding: 5px 10px; }
    .result { margin-top: 20px; }
    .thumbnail { margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    table, th, td { border: 1px solid #ddd; }
    th, td { padding: 10px; text-align: left; }
    th { background-color: #f2f2f2; }
    ul { padding-left: 20px; }
    li { margin-bottom: 5px; }
</style>
"""

bodyTemplate = """
<!DOCTYPE html>
<html>
<head>
    <title>DBpedia Search Engine</title>
    {{ styles|safe }}
</head>
<body>
    <h1>DBpedia Search Engine</h1>
    <form method="POST">
        <label for="searchTerm">Search Term:</label>
        <input type="text" id="searchTerm" name="searchTerm" required>
        <button type="submit">Search</button>
    </form>
    <input type="text" id="searchFilter" placeholder="Search...">

    <div class="result">
        <h2>Results for "{{ searchTerm }}":</h2>
        {% if thumbnail %}
            <div class="thumbnail">
                <img src="{{ thumbnail }}" alt="Thumbnail Image" style="max-width: 200px; max-height: 200px;">
            </div>
        {% endif %}
        {% if searchTerm %}
          <button onclick="printTTL('{{ searchTerm }}')">Print TTL File</button>
        {% endif %}
        <table id="resultsTable">
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody id="resultsTableBody">
                {% for property, values in results.items() %}
                    <tr class="result-row" data-property="{{ property }}">
                        <td>{{ property }}</td>
                        <td>
                            <ul>
                                {% for value in values %}
                                    <li>{{ value|safe }}</li>
                                {% endfor %}
                            </ul>
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
       function printTTL(searchTerm) {
          window.open('/printttl?searchTerm=' + searchTerm, '_blank').focus();
      }

      // Filter results on input change
      document.getElementById('searchFilter').addEventListener('input', function() {
          const filter = this.value.trim().toLowerCase();
          const tableRows = document.querySelectorAll('.result-row');
          tableRows.forEach(row => {
              const property = row.dataset.property.toLowerCase();
              const values = row.querySelectorAll('td ul li');
              let matchesProperty = property.includes(filter);
              let matchesValue = Array.prototype.some.call(values, value => value.textContent.toLowerCase().includes(filter));
              if (matchesProperty || matchesValue) {
                  row.style.display = '';
              } else {
                  row.style.display = 'none';
              }
          });
      });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        searchTerm = request.form.get("searchTerm").replace(" ", "_") if request.form.get("searchTerm") else None
        if searchTerm:
            try:
                results, thumbnail = search(searchTerm), formatResults(search(searchTerm))[1]
                return render_template_string(bodyTemplate, results=dict(sorted(formatResults(search(searchTerm))[0].items())), searchTerm=request.form.get("searchTerm"), thumbnail=thumbnail, styles=styles)
            except Exception as e:
                return "Error: " + str(e), 500
    return render_template_string(bodyTemplate, styles=styles)

@app.route("/printttl", methods=["GET"])
def printTTL():
    searchTerm = request.args.get("searchTerm").replace(" ", "_") if request.args.get("searchTerm") else None
    if searchTerm:
        try:
            ttl_content = printTtlResults(searchTerm)
            return ttl_content.serialize(format='ttl'), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except Exception as e:
            return "Error: " + str(e), 500
    return "No search term provided", 400

if __name__ == "__main__":
    app.run(debug=True)