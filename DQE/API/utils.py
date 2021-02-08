from DQE.Tester.Tester import *


def check_inputs(inputs):
    """
    Fucntion that checks if the inputs on the data that ins incoming from the POST request
    are correct and if not returns an error to the user
    """
    assert inputs.get('data') is not None
    assert inputs.get('tests') is not None
    assert isinstance(inputs.get('tests'), list)
    # manage error criation

def call_tester(inputs):
    """
    """
    # TODO understand how inputs come thru, so we can split them up and feed the kwargs to the function
    tester = Tester()
    data = inputs['data']
    tests = inputs['tests']
    schema_name = None
    for t in tests:
        for k,v in t.items():
            if k == "format_check":
                schema_name = v['schema_name']
                break

    return tester.run_tests(data=data, list_of_tests=tests, schema_name=schema_name)


def get_all_available_schemas():
    """
    function to get all schemas on the registry
    """
    return None