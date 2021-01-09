from flask import Flask, render_template, jsonify
from py2neo import Graph
from flask_cors import CORS
from views.family_graphql import FamilyGraphQl
from views.model import schema

cors = CORS()
app = Flask(__name__,static_folder='client/build',static_url_path='')
cors.init_app(app)
app.debug = True

graph_db = Graph("bolt://neo4j.fis.agh.edu.pl:7687", user="u6gwizdzk", password="290456")

app.add_url_rule('/api/family-tree',
                 view_func=FamilyGraphQl.as_view("family-tree", graph_db, schema=schema, batch=True, graphiql=True))

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'message': 'Endpoint Resource Not Found.'}), 404


@app.route('/')
def hello_world():
    return "Hello World"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
