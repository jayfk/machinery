# -*- coding: utf-8 -*-
import imp
import os, os.path

import django
from django.core.management import call_command

import cherrypy
from cherrypy.process import plugins

from django.core.handlers.wsgi import WSGIHandler
import logging

from cherrypy import _cplogging, _cperror
from django.http import HttpResponseServerError
from django.conf import settings
import platform
from unipath import Path


class HTTPLogger(_cplogging.LogManager):
    def __init__(self, app):
        _cplogging.LogManager.__init__(self, id(self), cherrypy.log.logger_root)
        self.app = app

    def __call__(self, environ, start_response):
        """
        Called as part of the WSGI stack to log the incoming request
        and its response using the common log format. If an error bubbles up
        to this middleware, we log it as such.
        """
        try:
            response = self.app(environ, start_response)
            self.access(environ, response)
            return response
        except:
            self.error(traceback=True)
            return HttpResponseServerError(_cperror.format_exc())

    def access(self, environ, response):
        """
        Special method that logs a request following the common
        log format. This is mostly taken from CherryPy and adapted
        to the WSGI's style of passing information.
        """
        atoms = {'h': environ.get('REMOTE_ADDR', ''),
                 'l': '-',
                 'u': "-",
                 't': self.time(),
                 'r': "%s %s %s" % (environ['REQUEST_METHOD'], environ['REQUEST_URI'], environ['SERVER_PROTOCOL']),
                 's': response.status_code,
                 'b': str(len(response.content)),
                 'f': environ.get('HTTP_REFERER', ''),
                 'a': environ.get('HTTP_USER_AGENT', ''),
        }
        for k, v in atoms.items():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif not isinstance(v, str):
                v = str(v)
            # Fortunately, repr(str) escapes unprintable chars, \n, \t, etc
            # and backslash for us. All we have to do is strip the quotes.
            v = repr(v)[1:-1]
            # Escape double-quote.
            atoms[k] = v.replace('"', '\\"')

        try:
            self.access_log.log(logging.INFO, self.access_log_format % atoms)
        except:
            self.error(traceback=True)


class DjangoAppPlugin(plugins.SimplePlugin):
    def __init__(self, bus, wsgi_http_logger=HTTPLogger):
        """ CherryPy engine plugin to configure and mount
        the Django application onto the CherryPy server.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.wsgi_http_logger = wsgi_http_logger

    def start(self):
        """ When the bus starts, the plugin is also started
        and we load the Django application. We then mount it on
        the CherryPy engine for serving as a WSGI application.
        We let CherryPy serve the application's static files.
        """
        cherrypy.log("Loading and serving the Django application")
        cherrypy.tree.graft(self.wsgi_http_logger(WSGIHandler()))
        static_handler = cherrypy.tools.staticdir.handler(
            section="/",
            dir=os.path.split(settings.CHERRYPY_ROOT)[1],
            root=os.path.abspath(os.path.split(settings.CHERRYPY_ROOT)[0])
        )
        cherrypy.tree.mount(static_handler, settings.STATIC_URL)


def setup():

    system = platform.system()
    if system == "Darwin":
        machine_bin = "/usr/local/bin/docker-machine"
    elif system == "Windows":
        machine_bin = "/bin/docker-machine"
    elif system == "Linux":
        machine_bin = "/usr/local/bin/docker-machine"
    else:
        # unsupported system
        raise NotImplementedError

    home = Path(os.path.expanduser("~"))
    machinery_home = home.child(".machinery")

    # create directories if they don't exist
    if not os.path.exists(machinery_home):
        os.mkdir(machinery_home)

    if not os.path.exists(machinery_home.child("media")):
        os.mkdir(machinery_home.child("media"))


    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "machinery.settings")
    os.environ.setdefault("MACHINERY_DEBUG", "True")
    os.environ.setdefault("MACHINERY_DOCKER_MACHINE_BIN", machine_bin)
    os.environ.setdefault("MACHINERY_DB", machinery_home.child("machinery.sqlite3"))
    os.environ.setdefault("MACHINERY_MEDIA_ROOT", machinery_home.child("media"))

    # run django.setup() to get started
    django.setup()

    # more import hints that rely on a ready django

    # create the cache table and run a migration
    call_command('createcachetable')
    call_command('migrate')

if __name__ == '__main__':

    setup()

    config = {
        'server.socket_port': 8090,
        'checker.on': False,
        'engine.autoreload.on': False
    }

    if os.environ.get("MACHINERY_RUN_GLOBAL"):
        config["server.socket_host"] = '0.0.0.0'

    cherrypy.config.update(config)

    DjangoAppPlugin(cherrypy.engine).subscribe()

    cherrypy.quickstart()