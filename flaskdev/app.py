from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress the InsecureRequestWarning if you are using verify_certs=False
warnings.simplefilter('ignore', InsecureRequestWarning)

app = Flask(__name__)

# Connect to Elasticsearch
es = Elasticsearch(
    "https://127.0.0.1:9200",
    basic_auth=('elastic', 'Bam352024647'),  # Consider using environment variables for credentials
    verify_certs=False
)

def search_recipes(query_text, page=1, size=10):
    """Search for recipes in Elasticsearch based on title or ingredient and filter duplicates by title."""
    query = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"ingredients.name": query_text}},  # Search in ingredients
                    {"match": {"title": query_text}}  # Search in title
                ],
                "minimum_should_match": 1  # At least one of the conditions should match
            }
        },
        "from": (page - 1) * size,  # Skip results for pagination
        "size": size  # Number of results per page
    }

    # Perform the search
    response = es.search(index='dessert-recipe', body=query)  # Adjust index name as needed
    
    # Log the raw response for debugging
    print("Elasticsearch Response:", response)
    
    recipes = []
    seen_titles = set()  # To track duplicate recipes by title
    for hit in response['hits']['hits']:
        recipe = hit['_source']

        # Check if the recipe title has already been seen
        if recipe['title'] not in seen_titles:
            recipes.append({
                'title': recipe['title'],
                'description': recipe.get('description', 'No description available.'),
                'preparation_time': recipe.get('preparation_time_minutes', 'N/A'),
                'cooking_time': recipe.get('cooking_time_minutes', 'N/A'),
                'ratings': recipe.get('ratings', 'N/A'),
                'ingredients': recipe.get('ingredients', []),
                'steps': recipe.get('steps', []),
                'created': recipe.get('created', 'N/A'),
                'image_url': recipe.get('image_url', 'default_image_url'),  # Default image URL
                'score': hit['_score']
            })
            seen_titles.add(recipe['title'])

    return recipes

@app.route('/')
def index():
    return render_template('searchpage.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query_text = data.get('query_text')  # Accepting 'query_text' instead of 'ingredient'
    recipes = search_recipes(query_text)  # Passing 'query_text' to the search_recipes function
    return jsonify(recipes)

@app.route('/TeamPage')
def teampage():
    return render_template('teampage.html')

@app.route('/searchpage')
def searchpage():
    return render_template('searchpage.html')

if __name__ == "__main__":
    app.run(debug=True, port=5005)
