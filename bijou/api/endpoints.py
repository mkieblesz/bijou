from flask import jsonify
from flask.views import MethodView

from bijou.exceptions import NotFoundException
from bijou.db.models.utils import get_class_by_tablename
from bijou.models import ScrapedModel


class BaseEndpoint(MethodView):
    def create_response(self, response, status=200):
        '''Helper function to create json response object'''
        json_response = jsonify(response)
        json_response.status_code = status
        return json_response


class ModelEndpoint(BaseEndpoint):
    '''Model endpoint'''

    def get(self, *args, **kwargs):
        tablename = kwargs['name']
        Klass = get_class_by_tablename(ScrapedModel, tablename)

        if Klass is None:
            raise NotFoundException()

        object_id = kwargs.get('id', None)
        if object_id is None:
            return self.create_response([instance.to_dict() for instance in Klass.query.all()])

        instance = Klass.get(id=object_id)
        if instance is not None:
            return self.create_response(instance.to_dict())

        raise NotFoundException()


class SwipeEndpoint(BaseEndpoint):
    def get(self, *args, **kwargs):
        pass
