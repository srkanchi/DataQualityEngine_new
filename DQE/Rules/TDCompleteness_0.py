
from DQE.Rules.RulesTemplate import RuleTemplate
import json
# from DQE.Utils.Weights import *
from DQE.Utils.mapping_scout_fields import *
import re

import pandas as pd
import os
import numpy as np 

import pprint


class TDCompleteness_0(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(TDCompleteness_0, self).__init__(rule_name='TDCompleteness_0', rule_category='data_quality')
    
    def _rule_input_check(self, data, inputs, schema=None):
        """
        """
        try:
            return 0
        except KeyError:
            print("For this rule to work, it has to have the input of `data`. Please refer to documentation.")
            return 1



    def _rule_definition(self, data, inputs, schema=None):
        version = "compl_TDs_V1.0.0"

        tptIdKey = data["trialDescriptions"][0].pop("tptIdKey")
        indication= self.get_indication(tptIdKey) 
        trialType = self.get_trial_type(tptIdKey)



        values = list(self.iterate_all(data,"value"))
        keys = list(self.iterate_all(data,"key"))

        dictFinal = dict(zip(keys, values))
#        pprint.pprint(dictFinal)

        dfRules = self.read_rules(tptIdKey, version, indication, trialType)

#        pprint.pprint(dfRules)


        cropsafetyException = self.exception_CROPSAFETY(dictFinal)
        missingFields = self.find_missing_fields(dfRules, dictFinal, cropsafetyException)
        scores= self.calculate_scores(dfRules, missingFields, indication, cropsafetyException)

        return {
            self.name: {"input": dictFinal, "version": version, "scores":scores, "missingFields":missingFields.tolist()
            }
        }




    def iterate_all(self, iterable, returned="key", prefix = "0"):                
        """Returns an iterator that returns all keys or values
        of a (nested) iterable.
        
        Arguments:
            - iterable: <list> or <dictionary>
            - returned: <string> "key" or "value"
            
        Returns:
            - <iterator>
        """
        nullCards = ['*','.','?']
        if isinstance(iterable, dict):
            index = 0

            for key, value in iterable.items():
                if returned == "key":
                    if(self.add_key(value)):                
                        yield key.strip() + "["+str(prefix)+"]"
 


                    for ret in self.iterate_all(value, returned=returned):
                        yield key + "[" +prefix+"]." + ret  
 
 

                elif returned == "value":
                    if not (isinstance(value, dict) or isinstance(value, list)):
                        if((value in nullCards) or (value is None)):
                            yield "Missing"
                        else:    
                            yield value 
                    else:
                        #This part was added to catch empty lists []
                        if(len(value)<1):
                            yield "Missing"


                    for ret in self.iterate_all(value, returned=returned):
                        yield ret

                else:
                    raise ValueError("'returned' keyword only accepts 'key' or 'value'.")


        elif isinstance(iterable, list):
            index = 0      
            for el in iterable:

                #This part was added to catch lists of string values (guidelines, keywords)
                if(returned == "value"):                
                    if not (isinstance(el, dict) or isinstance(el, list)):
                        strValue = ', '.join(iterable)
                        yield strValue
                        break
                #########        

                for ret in self.iterate_all(el, returned=returned, prefix=str(index)):
                    yield ret


                index = index + 1




    def add_key(self, value):                

        if(isinstance(value, list)):
            if(len(value)<1):

                return True
            else:

                for item in value:

                    if((isinstance(item, dict)) or (isinstance(item, list))):
                        return False
                    else:
                        return True
        elif(isinstance(value, dict)):                
            return False
        else:

            return True




    def read_rules(self, tptIdKey, version, indication, trialType):

        pathVersion = "DQE\CSV\\" + version + ".csv"
#        pathVersion = "./DQE/CSV/" + version + ".csv"

        df = pd.read_csv(pathVersion, index_col="Field", converters=None)

        conditions = [df[indication] == df[trialType], 
                      df[trialType] == df['EMEA']]
        

        choices = ['True', 'False']
        df['Required'] = np.select(conditions, choices, default='None')
        dfFiltered = df.query('Status == 0 & Required == "True"')

        return dfFiltered



    def find_missing_fields(self, dfRules, dictFinal, cropsafetyException):

        fields = dfRules.index.values

        if(cropsafetyException == True):
            fields = fields[fields != 'Target']

        for key, value in dictFinal.items():
            keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

            if(keyNoIndex in mappings):
                keyDF = mappings[keyNoIndex]
                if((keyDF in fields) & (value!="Missing")& (value!=False)):
                    fields = fields[fields != keyDF] # Remove all occurrences of elements with value keyDF from numpy array


        return fields




    def calculate_scores(self, dfRules, missingFields, indication, cropsafetyException):

        scores ={"rawScore":0, "weightedScore":0}
        countRowsMissing = len(missingFields)


        if(cropsafetyException == True):
            totalWeights = dfRules[dfRules['Exceptions']!="CROPSAFETY"][indication].sum()
            countRows = dfRules[dfRules['Exceptions']!="CROPSAFETY"][indication].count()
        else:
            totalWeights = dfRules[indication].sum()
            countRows= len(dfRules.index)


        totalMissing = 0

        for key in missingFields:
            totalMissing = totalMissing + int(dfRules.loc[[key],[indication]].values)

        scores["weightedScore"] = (totalWeights - totalMissing)/totalWeights
        scores["rawScore"] = (countRows - countRowsMissing)/countRows 

        return scores







    def exception_CROPSAFETY(delf, dictFinal):
        objective = dictFinal['trialDescriptions[0].keywords[0]']

        if objective.strip() == "CROPSAFETY":
            return True
        else:
            return False



    def get_indication(self, tptIdKey):
        indication = tptIdKey.strip()[0:1]
        if(indication not in ['I','F','H','S']):
            indication = 'Z'
 
        return indication

    def get_trial_type(self, tptIdKey):
        trialType = tptIdKey.strip()[1:2]
        if(trialType not in ['A','R','D']):
            trialType = 'TT'

        return trialType


    def find_field(delf, key):
        keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   # le quita el index al prefix    

        if(keyNoIndex not in mappings):
            return 'Not required'
        else:
            return mappings[keyNoIndex]


    def calculate_totals(delf, scores):
        scoresFinal= {"raw":0, "weight":0}

        totalFields = scores["countComplete"] +  scores["countMissing"]
        totalWeights = scores["scoreComplete"] +  scores["scoreMissing"]

        if((scores["countComplete"]> 0) & (totalFields>0)):
            scoresFinal["raw"] = (scores["countComplete"]/totalFields) * 100
        if((scores["scoreComplete"]> 0) & (totalWeights>0)):
            scoresFinal["weight"] = (scores["scoreComplete"]/totalWeights) * 100

        return scoresFinal