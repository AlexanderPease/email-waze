import os
import time
import tornado.options

# Environmenal settings for heroku#
# If you are developing for heroku and want to set your settings as environmental vars
# create settings_local_environ.py in the root folder and use:
# os.environ['KEY'] = 'value'
# to simulate using heroku config vars
# this is better than using a .env file and foreman
# since it still allows you to see logging.info() output.
# Make sure to also put import os in this settings_local_environ.py
try:
    import settings_local_environ
except:
    pass
    
time.tzset()

tornado.options.define("environment", default="dev", help="environment")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# These options differ by development environment
options = {
    'dev' : {
        'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 
            'port' : 27017, 
            'db' : os.environ.get('DB_NAME')
        },
        'base_url' : os.environ.get('BASE_URL'),
    },
    'prod' : {
        'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 
            'port' : 27017, 
            'db' : os.environ.get('DB_NAME')
        },
        'base_url' : os.environ.get('BASE_URL'),
    },
}

# These options are the same across all dev environments
default_options = {
    'project_root': os.path.abspath(os.path.join(os.path.dirname(__file__))),

    # Google API keys
    #'google_client_id': os.environ.get("GOOGLE_CLIENT_ID"),
    #'google_client_secret': os.environ.get("GOOGLE_CLIENT_SECRET"),

    'staff':[
        "alexander@usv.com",
        "me@alexanderpease.com",
        "jqgorelick@gmail.com"
    ],

    'module_dir': os.path.join(PROJECT_ROOT, 'templates/modules') #delete!
}

def get(key):
    # check for an environmental variable (used w Heroku) first
    if os.environ.get('ENVIRONMENT'):
        env = os.environ.get('ENVIRONMENT')
    else:
        env = tornado.options.options.environment

    if env not in options:
        raise Exception("Invalid Environment (%s)" % env)

    if key == 'environment':
        return env

    v = options.get(env).get(key) or os.environ.get(key.upper()) or default_options.get(key)

    if callable(v):
        return v

    if v is not None:
        return v

    return default_options.get(key)
