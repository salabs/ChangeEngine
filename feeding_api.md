# Here are exmaples for the feeding API body content

```
{
    "context": "the execution context (e.g. from which pipeline to not mix results from parallel tests)",
    "tests": [
        {
            "name": "Test case full name",
            "status": "PASS/FAIL",
            "repository": "repository (optional, for separating between tests with identical names)",
            "subtype": "type of test (optional, for separating test cases and for filtering subsets when prioritising",
            "fingerprint": "execution fingerprint (optional, for learning from changes in the execution fingerprint)"
        }
    ],
    "changes": [
        {
            "name": "string representing the changed item, for example file path",
            "repository": "repository (optional, for separating between changed items with identical names)",
            "item_type": "(optional, for separating items and for filtering subsets when prioritising)",
            "subtype": "(optional, for separating items for filtering subsets when prioritising"
        }
    ]
}
```
All optional fields will default to the value `default`.
Items in changes list can also be simply strings if optional values are not needed.
