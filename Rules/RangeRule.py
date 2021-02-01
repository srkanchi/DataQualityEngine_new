from Rules.RulesTemplate import RuleTemplate
##import deque

class RangeRule(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(RangeRule, self).__init__(rule_name='range_check', rule_category='data_integrity')
    
    def _rule_input_check(self, **kwargs):
        """
        """
        try:
            data = kwargs['data']
            upper = kwargs['upper_bound']
            lower = kwargs['lower_bound']
            if isinstance(upper, float) is False:
                raise ValueError("Upper bound value should be numeric.")
            if isinstance(lower, float) is False:
                raise ValueError("Lower bound value should be numeric.")
            return 0
        except KeyError:
            print("For this rule to work, it has to have the inputs of `data`, `upper_bound`, and `lower_bound`. Please refer to documentation.")
            return 1
        except ValueError:
            print("value should be numeric.")
            return 1

    def _rule_definition(self, **kwargs):
        """
        """
        data = kwargs.get('data')
        upper_bound = kwargs.get('upper_bound')
        lower_bound = kwargs.get('lower_bound')

        results = []
        
        flatten_dict = self.flatten_dict(data)

        for k, v in flatten_dict.items():
            if isinstance(v, float) or isinstance(v, int):
                if v >= upper_bound:
                    results.append({k: "FAIL"})
                elif v <= lower_bound:
                    results.append({k: "FAIL"})
                else:
                    results.append({k: "SUCCESS"})
        
        return {
            self.name: results
        }

