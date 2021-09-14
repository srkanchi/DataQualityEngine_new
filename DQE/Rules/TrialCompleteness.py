from DQE.Rules.RulesTemplate import RuleTemplate

import pandas as pd
import numpy as np 
import ast
import re
import sys
import os

import pprint




class TrialCompleteness(RuleTemplate):

    """
    class description here
    """

    def __init__(self):
        super(TrialCompleteness, self).__init__(rule_name='TrialCompleteness', rule_category='data_quality')
    
    def _rule_input_check(self, data, inputs, schema=None):
        """
        """
        try:
            assert data is not None
            weights = inputs['weights']
            version = inputs['version']
            attributeMapping = inputs['attributeMapping']

            if weights is None:
                raise ValueError("The weight matrix is empty.")
            if version is None:
                raise ValueError("The version is empty.")
            if attributeMapping is None:
                raise ValueError("The attribute mapping file is empty.")

            return 0

        except KeyError:
            print("For this rule to work, it has to have the input of `data`. Please refer to documentation.")
            return 1


    def _rule_definition(self, data, inputs, schema=None):
        tptIdKey = data["trialDescriptions"][0].pop("tptIdKey")
        weights = inputs.get('weights')
        version = inputs.get('version')
        attributeMapping = inputs.get('attributeMapping')
        version = inputs.get('version')


        indication= self.get_indication(tptIdKey) 
        trialType = self.get_trial_type(tptIdKey)


        values = list(self.iterate_all(data,"value"))
        keys = list(self.iterate_all(data,"key"))

        dictFinal = dict(zip(keys, values))
    

        df = self.read_rules(indication, trialType, weights)



        return {
            self.name: {"score":score, "mandatoryFields": mandatoryFields}
        }


        

