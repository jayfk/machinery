# -*- mode: python -*-
from unipath import Path
BASE_DIR = Path(os.getcwd())

hiddenimports = [
    "htmlentitydefs",
    "HTMLParser",
    "django.contrib.contenttypes.apps",
    "django.contrib.sessions.apps",
    "django.contrib.messages.apps",
    "django.contrib.staticfiles.apps",
    "django.contrib.sessions.serializers",
    "django.templatetags.i18n",
    "django.templatetags.static",
    "django.core.management.commands.migrate",
    "django.core.management.commands.sqlmigrate",
    "machines.context_processors",
    "crispy_forms.templatetags.crispy_forms_field",
    "machinery.settings",
    "crispy_forms_materialize",
]

a = Analysis([BASE_DIR.child("app").child("server.py")],
             pathex=[BASE_DIR],
             hiddenimports=hiddenimports,
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)

static = Tree(BASE_DIR.child('app').child('static'), prefix='static')
templates = Tree(BASE_DIR.child('app').child('templates'), prefix='templates')

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='machinery',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               static,
               templates,
               strip=None,
               upx=True,
               name='machinery')
