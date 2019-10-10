import json
import os
import sys

import database as db
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen

VERSION = 0.1

APP_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
STATIC_DIRECTORY = os.path.abspath(os.path.join(APP_DIRECTORY, 'static'))
TEMPLATES_DIRECTORY = os.path.abspath(os.path.join(APP_DIRECTORY, 'templates'))


def load_config_file(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


class Application(tornado.web.Application):
    def __init__(self, async_database, sync_database, config):
        handlers = [
            (r"/test/", TestStatusDataHandler),
            (r"/result/", ResultUpdateHandler),
            (r"/prioritize/", PrioritizeHandler),
        ]

        settings = dict(
            template_path=TEMPLATES_DIRECTORY,
            static_path=STATIC_DIRECTORY,
            debug=True,
        )
        self.async_db = async_database
        self.sync_db = sync_database
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def async_db(self):
        return self.application.async_db

    @property
    def sync_db(self):
        return self.application.sync_db

    @gen.coroutine
    def async_query(self, querer, *args, **kwargs):
        rows, formatter = querer(*args, **kwargs)
        rows = yield rows
        results = formatter(rows) if formatter else None
        if isinstance(rows, list):
            for connection in rows:
                connection.free()
        else:
            rows.free()
        return results

    def item_ids(self, changed_items, default_type='default'):
        item_ids = []
        for item in changed_items:
            if type(item) == str:
                name = item
                repository = 'default'
                item_type = default_type
                subtype = 'default'
            elif type(item) == dict:
                name = item['name']
                repository = item['repository'] if 'repository' in item else 'default'
                item_type = item['subtype'] if 'subtype' in item else default_type
                subtype = item['subtype'] if 'subtype' in item else 'default'
            else:
                raise Exception('Unsupported change items')

            item_id = self.sync_db.item_id(name, repository, item_type, subtype)
            if not item_id:
                item_id = self.sync_db.insert_item(name, repository, item_type, subtype)
            item_ids.append(item_id)
        return item_ids


class TestStatusDataHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        test_name = self.get_argument('name', None)
        if not test_name:
            self.set_status(400)
            self.write({"Error": "Missing test name"})
            return
        context = self.get_argument('context', 'default')
        repository = self.get_argument('repository', 'default')
        subtype = self.get_argument('subtype', 'default')
        test = yield self.async_query(self.async_db.test_item, test_name, repository, subtype, context)
        if test:
            self.write(test)
        else:
            self.set_status(404)
            arguments = {"name": test_name, "context": context, "subtype": subtype}
            self.write({"Error": "Test item not found", "arguments": arguments})


class ResultUpdateHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        context = data['context'] if 'context' in data else 'default'
        changed_item_ids = self.item_ids(data['changes'])
        for test in data['tests']:
            self.update_test_links(test, changed_item_ids, context)

    def update_test_links(self, test, changed_item_ids, context):
        test_name = test['name']
        repository = test['repository'] if 'repository' in test else 'default'
        subtype = test['subtype'] if 'subtype' in test else 'default'
        status = test['status']
        fingerprint = test['fingerprint'] if 'fingerprint' in test else 'default'

        test = self.sync_db.test_item(test_name, repository, subtype, context)
        if test:
            test_id = test['test_id']
            if test['status'] == status and changed_item_ids:
                self.sync_db.update_links(test_id, context, 0, changed_item_ids)
            elif changed_item_ids:
                self.sync_db.update_links(test_id, context, 1/len(changed_item_ids), changed_item_ids)
        else:
            test_id = self.sync_db.insert_test_case(test_name, repository, subtype)
        self.sync_db.update_previous_status(test_id, context, status, fingerprint)

class PrioritizeHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        data = json.loads(self.request.body)
        tests = data['tests']
        changes = data['changes']
        context = data['context'] if 'context' in data else 'default'
        changed_item_ids = self.item_ids(changes)
        if type(tests) == dict:
            repository = tests['repository']
            subtype = tests['subtype'] if 'subtype' in tests else 'default'
            prioritized = yield self.async_query(self.async_db.prioritize, context, repository, subtype, changed_item_ids)
        elif type(tests) == list:
            test_ids = self.item_ids(tests, 'test_case')
            prioritized = yield self.async_query(self.async_db.prioritize_test_list, context, test_ids, changed_item_ids)
        self.write({"tests": prioritized})


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("error: missing config file")
        exit(0)
    config = load_config_file(sys.argv[1])
    async_db = db.AsyncDatabase(config['db_host'],
                                config['db_name'],
                                config['db_user'],
                                config['db_password'])
    sync_db = db.SyncDatabase(config['db_host'],
                              config['db_name'],
                              config['db_user'],
                              config['db_password'])
    httpserver = tornado.httpserver.HTTPServer(Application(async_db, sync_db, config))
    httpserver.listen(int(config['port']))
    print("Server listening port {}".format(config['port']))
    tornado.ioloop.IOLoop.current().start()
