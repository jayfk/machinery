==========
Warning
==========
This project was a little experiment to port a django application to the desktop. It is no longer maintained.

.. image:: https://www.getmachinery.io/static/img/logo.png


==========
Quickstart
==========
You can run machinery as a docker container or as a standalone desktop application. Visit `getmachinery.io <http://www.getmachinery.io/get/>`_ to get started.


===============
About
===============
machinery is written in Python using the Django framework. Communication with docker-machine is done through the command line interface.

The standalone desktop application consists of two elements:

- A lightweight CherryPy webserver that runs the django applicaton
- Githubs Electron starts the webserver on localhost and opens a Window that renders the HTML/JS.

===============
Development
===============

If you are familiar with Python and Django, you can jump right in by installing all dependencies with

``pip install -r requirements/base.txt``

Create a cache table and run all initial migrations with

``python app/manage.py createcachetable``

``python app/manage.py migrate``

To start the debug server, run

``python app/manage.py runserver localhost:8090``

===============
Build
===============

**On OSX**

Clone the electron skeleton into the machinery folder

``git clone git@github.com:jayfk/machinery-skeleton.git``

Install appdmg as a global node package

``npm install -g appdmg``

Install all requirements

``pip install -r requirements/dev.txt``

and run

``python build.py osx``

There will be a ``machinery.app`` in ``skeleton/tmp`` containing your build and a ``machinery_latest.dmg`` in ``release/osx`` for distribution. 

You can run electron from the command line with

``skeleton/tmp/machinery.app/Contents/MacOS/Electron``

If you want to run the webserver without electron, run

``skeleton/tmp/machinery.app/Contents/Resources/app/machinery/machinery``

**On Windows**

Clone the electron skeleton into the machinery folder

``git clone git@github.com:jayfk/machinery-skeleton.git``

Install 7zip and make sure that the installation folder is in your path so that you can run ``7z`` directly from your terminal.

Install all requirements

``pip install -r requirements\dev.txt``

and run

``python build.py osx``

There will be a ``machinery`` folder inside ``skeleton\tmp`` containing your build and a ``machinery_latest.zip`` in ``release\win`` for distribution.

========
Security
========
machinery runs a webserver on 127.0.0.1:8090 without authentication/authorization, containing all you security 
credentials from various cloud providers, certificates etc. If you plan to run machinery on a remote host (e.g. with docker), make sure to set a nginx proxy with HTTP Basic Auth in front of it.

=====
Stack
=====
- `Django <https://www.djangoproject.com/>`_
- `SQLite <https://www.sqlite.org/>`_
- `Materialize <http://materializecss.com/>`_
- `CherryPy <http://www.cherrypy.org/>`_
- `Electron <https://github.com/atom/electron>`_
