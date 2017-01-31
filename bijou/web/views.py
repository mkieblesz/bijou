from flask.views import MethodView


class BaseView(MethodView):
    pass


class HomeView(BaseView):
    def get(self, *args, **kwargs):
        pass
