

from DQE.Rules.RulesTemplate import RuleTemplate
from DQE.Utils.completeness_TD_V1_0_0 import *
from DQE.Utils.mapping_scout_fields import *

import pandas as pd
import numpy as np 
import re
import sys

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
        pprint.pprint(dictFinal)


        df = self.read_rules(indication, trialType)

#        pprint.pprint(df)
        cropsafetyException = self.exception_CROPSAFETY(dictFinal)

        missingFields = self.find_missing_fields(df, dictFinal, cropsafetyException)
        scores= self.calculate_scores(df, missingFields, indication, cropsafetyException)





        return {
            self.name: {"input": dictFinal, "scores":scores, "missingFields":missingFields.tolist()
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



    def calculate_scores(self, dfRules, missingFields, indication, cropsafetyException):

        try:

            scores ={"rawScore":0, "weightedScore":0}
            countRowsMissing = len(missingFields)

            if(cropsafetyException == True):
                totalWeights = dfRules[dfRules["Exception"]!="CROPSAFETY"]["Weight"].sum()
                countRows = dfRules[dfRules["Exception"]!="CROPSAFETY"]["Weight"].count()
            else:
                totalWeights = dfRules["Weight"].sum()
                countRows= len(dfRules.index)


            totalMissing = 0

            for key in missingFields:
                totalMissing = totalMissing + int(dfRules.loc[[key],["Weight"]].values)

            scores["weightedScore"] = (totalWeights - totalMissing)/totalWeights
            scores["rawScore"] = (countRows - countRowsMissing)/countRows 


        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])

        return scores





    def find_missing_fields(self, dfRules, dictFinal, cropsafetyException):

        try:

            fields = dfRules.index.values

            if(cropsafetyException == True):
                fields = fields[fields != 'Target']

            for key, value in dictFinal.items():
                keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

                if(keyNoIndex in mappings):
                    keyDF = mappings[keyNoIndex]
                    if((keyDF in fields) & (value!="Missing")& (value!=False)):
                        fields = fields[fields != keyDF] # Remove all occurrences of elements with value keyDF from numpy array

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])

        return fields






    def exception_CROPSAFETY(delf, dictFinal):
        try:
            objective = dictFinal['trialDescriptions[0].keywords[0]']

            if objective.strip() == "CROPSAFETY":
                caseException = True
            else:
                caseException = False

        except pd.errors.EmptyDataError:
            caseException = False

        return caseException



    def read_rules(self, indication, trialType):
        try:
            df = pd.read_csv(dfWeights, delimiter=",", index_col="Field", converters=None)
            dfFiltered = df.loc[(df["Status"] == 0) & (df["Trial"] == trialType) & (df["Indication"] == indication)]

        except pd.errors.EmptyDataError:
            dfFiltered = pd.DataFrame()

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])

        return dfFiltered



    def get_indication(self, tptIdKey):

        indication = tptIdKey.strip()[0:1]

        if(indication not in ['I','F','H','S']):
            indication = 'II'

        return indication





    def get_trial_type(self, tptIdKey):

        trialType = tptIdKey.strip()[1:2]
        if(trialType not in ['A','R','D']):
            trialType = 'TT'

        return trialType
