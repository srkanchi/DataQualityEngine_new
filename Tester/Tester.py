from Rules.RulesFactory import RulesFactory
from Schema.Schema import SchemaHandler


class Tester(object):
    """
    Describe the claass here
    """

    def __init__(self):
        """
        class constructor
        """
        self.rules_factory = RulesFactory()
        self.schema_handler = SchemaHandler()
    
    def __run_test(self, test_name, data, schema_name=None):
        rule = self.rules_factory.get_rule(test_name)
        if test_name == 'format_check':
            schema = self.schema_handler.get_schema(schema_name)
        rule_results = rule.run_rule(data=data, schema=schema_name)
        return rule_results

    def run_tests(self, list_of_tests, data, schema_name=None):
        rtn = []
        for t in list_of_tests:
            rtn.append(self.__run_test(t, data, schema_name))
        return rtn
