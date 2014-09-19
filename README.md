Ansatz.me
=================

Crowdsourcing an email white pages

To get environment, run: pip install -r requirements.txt

To start local server, run: python tornado_server.py

To run locally, you need a file named settings_local_environ.py that includes environment variables, like this: 
os.environ['DB_NAME'] = 'heroku_appblarg39845748967'

Technology
===========

Built with:

 * Python / [Tornado](http://tornadoweb.org)
 * [Mongodb](http://www.mongodb.com/)
 * [GMail](http://gmail.com)
 * [Celery](http://www.celeryproject.org/)
 * [RabbitMQ](http://www.rabbitmq.com) (broker for Celery)