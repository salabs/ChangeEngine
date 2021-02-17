
TEST_CASE = """
SELECT item.id as test_id, item.name, subtype, repository,
       context, status, fingerprint,
       previous_status.last_updated
FROM item
LEFT OUTER JOIN previous_status ON previous_status.test=item.id
                               AND context=%(context)s
WHERE item_type='test_case'
  AND item.name=%(test_name)s
  AND subtype=%(subtype)s
  AND repository=%(repository)s
"""

INSERT_ITEM = """
INSERT INTO item(repository, name, item_type, subtype)
VALUES (%(repository)s, %(name)s, %(item_type)s, %(subtype)s)
RETURNING id
"""

ITEM_ID = """
SELECT id
FROM item
WHERE name=%(name)s AND item_type=%(item_type)s AND subtype=%(subtype)s
"""

UPSERT_PREVIOUS_STATUS = """
INSERT INTO previous_status(test, context, status, fingerprint, last_updated, execution_id)
    VALUES (%(test)s, %(context)s, %(status)s, %(fingerprint)s, 'now', %(execution_id)s)
ON CONFLICT (test, context)
DO UPDATE
    SET status=%(status)s, fingerprint=%(fingerprint)s, last_updated='now', execution_id=%(execution_id)s
"""

def update_links(alpha, strength, effected_item, changed_items):
    VALUES_ROW = "({effected_item}, {strength}, {changed_item}, %(context)s, 'now')"
    value_rows = []
    for item_id in changed_items:
        value_rows.append(VALUES_ROW.format(strength=strength, changed_item=item_id,
                                            effected_item=effected_item))
    return """
INSERT INTO link(effected_item, strength, changed_item, context, last_updated)
    VALUES {value_rows}
ON CONFLICT (effected_item, changed_item, context)
DO UPDATE
    SET strength=link.strength*{alpha} + (1 - {alpha}) * {strength}, last_updated='now'
""".format(value_rows=',\n'.join(value_rows),
           alpha=float(alpha),
           strength=float(strength))

TEST_ID_SUBQUERY = """
SELECT id
FROM item
WHERE repository=%(repository)s
  AND item_type='test_case'
  AND subtype=%(subtype)s
"""

def prioritize(use_test_list=True):
    return """
SELECT item.id, item.name, repository, item_type, subtype,
       status, sum(strength) as strength
FROM item
LEFT OUTER JOIN previous_status ON previous_status.test=item.id
                               AND previous_status.context=%(context)s
LEFT OUTER JOIN link ON link.effected_item=item.id
                    AND link.context=%(context)s
                    AND link.changed_item IN %(changed_item_ids)s
WHERE item.id IN {test_ids}
GROUP BY item.id, item.name, repository, item_type, subtype, status
ORDER BY strength DESC NULLS LAST, status NULLS LAST
""".format(test_ids="%(test_ids)s" if use_test_list else "({})".format(TEST_ID_SUBQUERY))


def last_update(context):
    return """
SELECT
	DISTINCT ON (previous_status.execution_id) execution_id,
	previous_status.context,
	previous_status.last_updated,
	item.repository,
	item.item_type,
	item.subtype
FROM previous_status
INNER JOIN item ON item.id=previous_status.test
WHERE previous_status.context='{}'""".format(context)
