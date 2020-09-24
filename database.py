import asyncio
import datetime
import urllib.parse

import queries

import sql_queries

# Learning coefficient for the link strength calculation
ALPHA = 0.9

class SyncDatabase(object):
    def __init__(self, host, dbname, user, password):
        connection_uri = 'postgresql://{user}:{pw}@{host}/{dbname}'.format(
            user=user.strip(),
            pw=urllib.parse.quote_plus(password),
            host=host.strip().rstrip('/'),
            dbname=dbname.strip(),
        )
        self.session = queries.Session(connection_uri)

    def insert_test_case(self, test_name, repository, subtype):
        return self.insert_item(test_name, repository, 'test_case', subtype)

    def insert_item(self, name, repository, item_type, subtype):
        values = {'name': name, 'repository': repository, 'item_type': item_type, 'subtype': subtype}
        return single_value(self.session.query(sql_queries.INSERT_ITEM, values))

    def test_item(self, test_name, repository, subtype, context):
        values = {'test_name': test_name, 'repository': repository, 'context': context, 'subtype': subtype}
        return single_dict(self.session.query(sql_queries.TEST_CASE, values))

    def item_id(self, name, repository, item_type, subtype):
        values = {'name': name, 'item_type': item_type, 'subtype': subtype, 'repository': repository}
        return single_value(self.session.query(sql_queries.ITEM_ID, values))

    def update_previous_status(self, test_id, context, status, fingerprint):
        values = {'test': test_id, 'context': context, 'status': status, 'fingerprint': fingerprint}
        self.session.query(sql_queries.UPSERT_PREVIOUS_STATUS, values)

    def update_links(self, effected_item, context, strength, changed_items):
        values = {'context': context}
        sql = sql_queries.update_links(ALPHA, strength, effected_item, changed_items)
        self.session.query(sql, {'context': context})

class AsyncDatabase:

    def __init__(self, host, dbname, user, password):
        connection_uri = 'postgresql://{user}:{pw}@{host}/{dbname}'.format(
            user=user.strip(),
            pw=urllib.parse.quote_plus(password),
            host=host.strip().rstrip('/'),
            dbname=dbname.strip(),
        )
        if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.session = queries.TornadoSession(connection_uri)

    def test_item(self, test_name, repository, subtype, context):
        values = {'test_name': test_name, 'repository': repository, 'context': context, 'subtype': subtype}
        return self.session.query(sql_queries.TEST_CASE, values), single_dict

    def item_id(self, name, repository, item_type, subtype):
        values = {'name': name, 'item_type': item_type, 'subtype': subtype, 'repository': repository}
        return self.session.query(sql_queries.ITEM_ID, values), single_value

    def prioritize_test_list(self, context, test_ids, changed_item_ids):
        values = {'context': context, 'test_ids': tuple(test_ids),
                  'changed_item_ids': tuple(changed_item_ids)}
        return self.session.query(sql_queries.prioritize(use_test_list=True), values), dict_formatter

    def prioritize(self, context, repository, subtype, changed_item_ids):
        values = {'context': context, 'repository': repository, 'subtype': subtype,
                  'changed_item_ids': tuple(changed_item_ids)}
        return self.session.query(sql_queries.prioritize(use_test_list=False), values), dict_formatter


def list_formatter(rows):
    results = []
    for row in rows:
        values = [row[key] for key in row]
        results.append(values if len(values) > 1 else values[0])
    return results

def single_value(rows):
    return list_formatter(rows)[0] if rows else None

def dict_formatter(rows):
    results = []
    for row in rows:
        for key in row:
            if type(row[key]) in (datetime.time, datetime.date, datetime.datetime, datetime.timedelta):
                row[key] = str(row[key])
        results.append(row)
    return results

def single_dict(rows):
    return dict_formatter(rows)[0] if rows else None


if __name__ == '__main__':
    pass
