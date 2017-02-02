import os
import subprocess

from flask import current_app, url_for, redirect, render_template
from flask.views import MethodView

from bijou.config.default import base_dir


class BaseView(MethodView):
    pass


class HomeView(BaseView):
    def get(self, *args, **kwargs):
        return render_template('home.html')


class ScrapeStreamView(BaseView):
    def get(self, *args, **kwargs):
        def log_generator():
            with open(os.path.join(base_dir, 'output.log')) as f:
                while True:
                    yield f.read()

        return current_app.response_class(log_generator(), mimetype='text/plain')


class ScrapeView(BaseView):
    def get(self, *args, **kwargs):
        cmd = "ps -eo pid,command | grep 'make scrape' | grep -v grep | awk '{print $1}'"
        scraper_running = subprocess.check_output(cmd, shell=True).decode('utf-8').strip() != ''
        if scraper_running is False:
            subprocess.Popen("make scrape", stderr=subprocess.STDOUT)

        return redirect(url_for('homeview'))
