#Querying tests from sinle repository

The body looks similar as in the [feeding.api](feeding_api.md), because API is also using the `changes` and the
`context` keys in identical manner. But because API is querying test, we do not the `tests` contains only the 
`repository` and  `subtype` keys. 

```
{
    "context": "the execution context (e.g. from which pipeline to not mix results from parallel tests. Supports LIKE operator from SQL engine, example %)" ,
    "tests": {
        "repository": "Repository ",
        "subtype": "type of test (optional, for separating test cases and for filtering subsets when prioritising",
    },
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
