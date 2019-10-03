*** Settings ***
Library         REST    http://localhost:${PORT}

*** Variables ***
${PORT}=  8888
${CHANGE_DATA1}=  { "name": "Test case full name",
...                 "status":"PASS",
...                 "changes": [] }
${CHANGE_DATA2}=  { "name": "Test case full name",
...                 "status":"FAIL",
...                 "changes": ["foo", "bar", {"name": "foobar", "repository": "foo"}] }
${CHANGE_DATA3}=  { "name": "Test case full name",
...                 "status":"PASS",
...                 "changes": ["foo", "bar", "foobar"] }
${CHANGE_DATA4}=  { "name": "Test case full name",
...                 "status": "FAIL",
...                 "changes": [] }


${PRIORITIZATION_DATA}=  { "context": "default",
...                        "tests": ["Test case full name", "Suite.Main page", "Other test"],
...                        "changes": ["foo", "bar"] }

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

Prioritization api works
    POST                /prioritize/    ${PRIORITIZATION_DATA}
    Integer             response status  200
    Array               $.tests
