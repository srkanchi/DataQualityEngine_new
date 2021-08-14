# DataQualityEngine
### Steps
1. Run `server-api.py`. If run the codes on local, using port 8005
2. Go to `tests`, run `python request_post.py`. This will use `input_example.json` as input, against the rules: ` DataQualityEngine/DQE/Rules/RangeRule.py`
3. Input format:
```
{
    "data": {
        "colA": "testA",
        "colB": 1000,
        "colC": 123.123,
        "colD": [1,2,3, "testD"],
        "colE": {
            "col_colEA": "testEA"
        },
        "colF": 15.0
    },
    "tests": [
        {"range_check": {
            "upper_bound": 100.0,
            "lower_bound": 0.0
            }
        }
    ]
}
```
4. Expect results:
```The pastebin URL is:[
  {
    "range_check": [
      {
        "colB": "FAIL"
      },
      {
        "colC": "FAIL"
      },
      {
        "colF": "SUCCESS"
      }
    ]
  }
]
```
