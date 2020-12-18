


class RuleTemplate(object):
    """
    """

    def __init__(self, rule_name, rule_category=None, application_specific=None, application_specific_name=None):
        """
        class constructor
        """
        self.name = rule_name
        self.category = rule_category
        self.application_specific = application_specific
        self.application_specific_name = application_specific_name

        if self.application_specific is not None and self.application_specific_name is None:
            raise ValueError("If rule is application specific, the application name must be provided!")
            
        if self.name is None:
            raise ValueError("Rule must have a name!")
    
    @abstractmethod
    def _rule_definition(self, **kwargs):
        """
        Specific implementation of the rule
        """
        pass

    @abstractmethod
    def _rule_input_check(self, **kwargs):
        """
        """
        pass

    def run_rule(self, **kwargs):
        """
        Run the defined rule
        """
        # can perform extra transformatiosn that are shared across different rules
        rtn = self._rule_definition(kwargs)
        return rtn
