from Rules.RulesTemplate import RuleTemplate


class RangeRule(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(RangeRule, self).__init__(rule_name='range_check', rule_category='data_integrity')
    
    def _rule_input_check(self, **kwargs):
        """
        """
        return None

    def _rule_definition(self, **kwargs):
        """
        """
        data = kwargs.get('data')
        upper_bound = kwargs.get('upper_bound')
        lower_bound = kwargs.get('lower_bound')

        results = None
        # run the checks!
        return results
