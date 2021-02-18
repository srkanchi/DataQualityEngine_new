### Rules Template class 
from abc import ABC, abstractmethod
import collections


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
    def _rule_definition(self, data, inputs, schema=None):
        """
        Specific implementation of the rule
        """         
        pass     

    @abstractmethod
    def _rule_input_check(self, data, inputs, schema=None):
        """
        checks if rules exist in 
        """
        ## rules directory 
        pass

    def flatten_dict(self, data, parent_key='', sep='_'):
        items = []
        for k, v in data.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def run_rule(self, data, inputs, schema=None):
        """
        Run the defined rule
        """
        # can perform extra transformatiosn that are shared across different rules
        if self._rule_input_check(data, inputs, schema) == 1:
            print("ERROR ON RULE INPUT. IGNORING IT.")
            return None
        else:
            rtn = self._rule_definition(data, inputs, schema)
            return rtn
