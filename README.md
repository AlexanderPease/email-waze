Ansatz.me
=================

Crowdsourcing an email white pages


Local Development
=================

Before setting up local environment, install:
- virtualenvwrapper (http://virtualenvwrapper.readthedocs.org/en/latest/install.html)
- npm (https://github.com/npm/npm)


To set up local environment, run:

1. pip install -r requirements.txt
2. npm install


For CSS and JS development, run:

1. grunt watch


To start local server*, run:

1. python tornado_server.py

*To run locally, you need a file named settings_local_environ.py that includes environment variables, like this: 
os.environ['DB_NAME'] = 'heroku_appblarg39845748967'



Technology
===========

Built with:

 * Python / [Tornado](http://tornadoweb.org)
 * [Mongodb](http://www.mongodb.com/)
 * [GMail](http://gmail.com)
 * [Celery](http://www.celeryproject.org/)
 * [RabbitMQ](http://www.rabbitmq.com) (broker for Celery)