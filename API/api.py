# using flask_restful
from flask import Flask, jsonify, Response
from flask_restful import Resource, Api, reqparse
from API.utils import *

parser = reqparse.RequestParser()
parser.add_argument('data')

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)


class Hello(Resource):

    def get(self):
        return jsonify({'message': 'Hello from DQEngine'})


class RunTests(Resource):

    def post(self):
        args = parser.parse_args()
        check_inputs(args)
        rtn = call_tester(args)
        return jsonify(rtn)

class ListSchemas(Resource):
    def get(self):
        return jsonify(get_all_available_schemas())


# adding the defined resources along with their corresponding urls
api.add_resource(Hello, '/')
api.add_resource(RunTests, '/runTests')

# driver function
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8005)

