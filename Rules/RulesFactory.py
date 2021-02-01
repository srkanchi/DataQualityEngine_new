import importlib
import os
from glob import glob


class RulesFactory(object):
    """
    """
    def __init__(self):
        """
        class constructor
        """
        self.rule_dict = {}
        self._read_all_files()
        
    def _read_all_files(self):
        """
        reads all files in the Rules folder that are not the factory nor the Template and instanciates it
        """
        # Step 1 read all files
        # Step 2 instanciates each file/class and save it to self dictionary
        # self.rule_repository = all_classes
        module = importlib.import_module('Rules')
        for file in os.listdir("./Rules/"):
            name = os.path.splitext(os.path.basename(file))[0]
            print(name)
            if name not in ['__init__', 'RulesTemplate', 'RulesFactory', '__pycache__']:
                my_class = getattr(module, name)
                my_instance = my_class()
                self.rule_dict[my_instance.name] = my_instance
                
    def get_rule(self, rule_name):
        """
        """
        return self.rule_dict[rule_name]
    
    def list_rules_available(self):
        """
        """
        return list(self.rule_dict.keys())                    