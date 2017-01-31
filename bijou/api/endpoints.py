from flask import jsonify
from flask.views import MethodView


class BaseEndpoint(MethodView):
    def create_response(self, response, status=200):
        '''Helper function to create json response object'''
        json_response = jsonify(response)
        json_response.status_code = status
        return json_response


class ModelEndpoint(BaseEndpoint):
    '''Model endpoint with serializer'''
    def get(self, *args, **kwargs):
        pass
