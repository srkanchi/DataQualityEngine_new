from Tester.Tester import *



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
    # data?
    # schema_name
    # testes to run from teh API
    return tester.run_tests()


def get_all_available_schemas():
    """
    function to get all schemas on the registry
    """
    return None