# using flask_restful
from flask import Flask, jsonify, Response
from flask_restful import Resource, Api, reqparse, request
from DQE.API.utils import *

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)


class Hello(Resource):

    def get(self):
        return jsonify({'message': 'Hello from DQEngine'})


class RunTests(Resource):

    def post(self):
        json_data = request.get_json(force=True)
        check_inputs(json_data)
        rtn = call_tester(json_data)
        return jsonify(rtn)
        # return jsonify({'message': 'Hello from POST'})


# adding the defined resources along with their corresponding urls
api.add_resource(Hello, '/')
api.add_resource(RunTests, '/run')

# driver function
if __name__ == '__main__':
    #from waitress import serve
    # serve(app, host="0.0.0.0", port=8005)
    app.run(host='0.0.0.0', port=8005 ,debug=True) ## run on local machine
    # app.run(host='0.0.0.0', port=10020 ,debug=True)

