from DQE.Rules.RulesFactory import RulesFactory
from DQE.Schema.Schema import SchemaHandler


class Tester(object):
    """
    Tester class where tests are accepted. After running tests, results are returned 
    """

    def __init__(self):
        """
        class constructor
        """
        self.rules_factory = RulesFactory()
        self.schema_handler = SchemaHandler()
    
    ## single run test
    def __run_test(self, test_name, data, inputs, schema_name=None):
        rule = self.rules_factory.get_rule(test_name)
        if test_name == 'format_check':
            schema = self.schema_handler.get_schema(schema_name)
        rule_results = rule.run_rule(data=data, inputs=inputs, schema=schema_name)
        return rule_results
    
    ## multiple tests 
    def run_tests(self, list_of_tests, data, schema_name=None):
        rtn = []
        for t in list_of_tests:
            rtn.append(self.__run_test(test_name=list(t.keys())[0], 
                                       data=data, 
                                       inputs=list(t.values())[0], 
                                       schema_name=schema_name))
        return rtn
