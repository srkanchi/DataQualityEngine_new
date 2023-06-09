from DQE.Rules.RulesTemplate import RuleTemplate


class FormatCheck(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(FormatCheck, self).__init__(rule_name='format_check', rule_category='data_integrity')
    
    def _rule_input_check(self, data, schema, inputs):
        """
        """
        try:
            assert data is not None
            schema_name = inputs['schema_name']
            return 0
        except KeyError:
            print("For this rule to work, it has to have the inputs of `data` and `schema_name`. Please refer to documentation.")
            return 1


    def _rule_definition(self, data, schema, inputs):
        """
        """
        schema_name = inputs.get('schema_name')
        results = None
        
        # check if data is the same format as the avro schema use avro-validator

        return results
