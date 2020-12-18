

class RulesFactory(object):
    """
    """

    def __init__(self):
        """
        class constructor
        """
        self.rule_dict = {}
        """
        rule_repository = {
            "rule_name": rule_class,
            "range_check": RangeRule(...)
        }
        """

    
    def _read_all_files(self):
        """
        reads all files in the Rules folder that are not the factory nor the Template and instanciates it
        """
        # Step 1 read all files
        # Step 2 instanciates each file/class and save it to self dictionary
        # self.rule_repository = all_classes
    
    def get_rule(self, rule_name):
        """
        """
        return self.rule_dict[rule_name]

