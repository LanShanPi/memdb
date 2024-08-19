from flask import Flask, jsonify
from flask_cors import CORS
import weaviate

app = Flask(__name__)
CORS(app)  # 启用 CORS

client = weaviate.Client(
    url="http://localhost:8080",
    auth_client_secret=weaviate.AuthApiKey(api_key="WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih")
)

@app.route('/api/data', methods=['GET'])
def get_data():
    schema_info = client.schema.get("User_123")
    nodes = [{"id": prop['name'], "group": 2} for prop in schema_info['properties']]
    nodes.append({"id": "Class", "group": 1})
    links = [{"source": "Class", "target": prop['name']} for prop in schema_info['properties']]
    print(links)
    return jsonify({"nodes": nodes, "links": links})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8592)
