from os import environ
from paste.deploy import loadapp
from waitress import serve

if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)
