

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
    return None


def get_all_available_schemas():
    """
    function to get all schemas on the registry
    """
    return None