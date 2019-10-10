*** Settings ***
Library         REST    http://localhost:${PORT}

*** Variables ***
${PORT}=  8888
${CHANGE_DATA1}=  { "tests": [{"name": "Test case full name", "status": "PASS"}],
...                 "changes": [] }
${CHANGE_DATA2}=  { "tests": [{"name": "Test case full name", "status": "FAIL"}],
...                 "changes": ["foo", "bar", {"name": "foobar", "repository": "foo"}] }
${CHANGE_DATA3}=  { "tests": [{"name": "Test case full name", "status": "FAIL"}],
...                 "changes": ["foo", "bar", "foobar"] }
${CHANGE_DATA4}=  { "tests": [{"name": "Test case full name", "status": "FAIL"}],
...                 "changes": [] }

${PRIORITIZATION_DATA_WITH_TESTLIST}=
...     { "context": "default",
...       "tests": ["Test case full name", "Suite.Main page", "Other test"],
...       "changes": ["foo", "bar"] }

${PRIORITIZATION_DATA_WITHOUT_TESTLIST}=
...     { "context": "default",
...       "tests": {"repository": "default"},
...       "changes": ["foo", "bar"] }

*** Test cases ***

Existing test case data can be queried
    GET                 /test/?name=Suite.Main%20page
    Integer             response status         200
    Object              $
    String              $.name
    Integer             $.test_id

Quering non existing test case data gives error message
    GET                 /test/?name=Suite.Not%20Exist
    Integer             response status         404
    Object              $
    String              $.Error

Test results can be posted
    POST                /result/    ${CHANGE_DATA1}
    Integer             response status  200
    POST                /result/    ${CHANGE_DATA2}
    Integer             response status  200
    POST                /result/    ${CHANGE_DATA3}
    Integer             response status  200
    POST                /result/    ${CHANGE_DATA4}
    Integer             response status  200

Prioritization api works with test list
    POST                /prioritize/    ${PRIORITIZATION_DATA_WITH_TESTLIST}
    Integer             response status  200
    Array               $.tests
    #Output              response body

Prioritization api works without test list
    POST                /prioritize/    ${PRIORITIZATION_DATA_WITHOUT_TESTLIST}
    Integer             response status  200
    Array               $.tests
    #Output              response body
