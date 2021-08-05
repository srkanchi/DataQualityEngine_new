from DQE.Rules.RulesTemplate import RuleTemplate
import json
# from DQE.Utils.Weights import *
from DQE.Utils.mapping_scout_fields import *
import re

import pandas as pd
import os
import numpy as np 

import pprint

class TDCompleteness_1(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(TDCompleteness_1, self).__init__(rule_name='TDCompleteness_1', rule_category='data_quality')
    
    def _rule_input_check(self, data, inputs, schema=None):
        """
        """
        try:
            return 0
        except KeyError:
            print("For this rule to work, it has to have the inputs of `data`, `upper_bound`, and `lower_bound`. Please refer to documentation.")
            return 1
        except ValueError:
            print("value should be numeric.")
            return 1



    def _rule_definition(self, data, inputs, schema=None):

        tptIdKey = data["trialDescriptions"][0].pop("tptIdKey")
#        plannedAssessments = data["trialDescriptions"][0].pop("plannedAssessments")

        values = list(self.iterate_all(data,"value"))
        keys = list(self.iterate_all(data,"key"))

        dictFinal = dict(zip(keys, values))
#        pprint.pprint(dictFinal)

        dfRules = self.read_rules()


        self.find_weights(dfRules, dictFinal, tptIdKey)

#        self.check_planned_assessments("plannedAssessments",plannedAssessments, dfRules, indication)






        print(">>>>>>>>>>>>>>>>>>>>>>>>>> ")
        pprint.pprint(dictFinal)


#        print("matrix ", dfRules)


#        print(*(list(self.iterate_all(data,"key"))), sep = "\n")
#        print(*(list(self.iterate_all(data,"value"))), sep = "\n")

        return {
            self.name: {"totalsAssess":0
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
            for key, value in iterable.items():
#                if returned == "key":
                if returned == "key":
                    if(self.add_key(value)):
                        yield key.strip()

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




    def read_rules(self):
        df = pd.read_csv('DQE\CSV\compl_TDs_V1.0.0.csv', index_col="Field", converters=None)
        return df





    def find_weights(self, dfRules, dictFinal, tptIdKey):

#        tpt_id_key = dictFinal["trialDescriptions[0].tptIdKey"]

        indication= tptIdKey.strip()[0:1]
        trialType = tptIdKey.strip()[1:2]

        pprint.pprint(dfRules)

        scores ={"general":0, "assessments":0, "application":0, "missing":0}

        for key, value in dictFinal.items():
            dictKey= self.find_mapping(key)

            scoreInd = int(dfRules.loc[[dictKey],[indication]].values)
            scoreTrial= int(dfRules.loc[[dictKey],[trialType]].values)
            ruleSection = (dfRules.loc[[dictKey],["Section"]].values)[0][0]            
            exception = (dfRules.loc[[dictKey],["Exceptions"]].values)[0][0]            



# ORIGINALES !
#            if(scoreInd != scoreTrial):
#                dictFinal[key]= "Not required"
#            else:
#                if((isinstance(value, list)) or (value != "Missing")):
#                    scores[ruleSection]= scores[ruleSection] + scoreInd
#                else:
#                    scores["missing"]= scores["missing"] + scoreInd


            if(scoreInd != scoreTrial):
                dictFinal[key]= "Not required"
            else:

                if(exception=="PHSES"):                        
                    if(self.exception_PHSES(key, value, dictFinal) == True):
                        dictFinal[key]= "Not required"
                        break

                if((isinstance(value, list)) or (value != "Missing")):
                    scores[ruleSection]= scores[ruleSection] + scoreInd
                else:
                    scores["missing"]= scores["missing"] + scoreInd


        print("scores ", scores)















    def exception_PHSES(delf, key, value, dictFinal):
        pathSE = ".".join(key.split(".", 2)[:2])
        pathSE = pathSE + ".standardEvaluationId"

        SE = (dictFinal[pathSE]).strip()[0:1]

        if(SE != value):
            if((SE == "P") or(SE == "H")):
                return True
            else:
                return False
        else:
            return False





    def find_mapping(delf, key):
        keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   # le quita el index al prefix    
        return mappings[keyNoIndex]





# Enteoria esta completo, pero genera mas keys que las necesarias 
#        nullCards = ['*','.','?']
#        if isinstance(iterable, dict):
#            for key, value in iterable.items():
#                if returned == "key":
#                    yield key

#                    for ret in self.iterate_all(value, returned=returned):
#                        yield key + "[" +prefix+"]." + ret 


#                elif returned == "value":
#                    if not (isinstance(value, dict) or isinstance(value, list)):
#                        if((value in nullCards) or (value is None)):
#                            yield "Missing"
#                        else:    
#                            yield value 
#                    else:
                        #This part was added to catch empty lists []
#                        if(len(value)<1):
#                            yield "Missing"


#                    for ret in self.iterate_all(value, returned=returned):
#                        yield ret
#                else:
#                    raise ValueError("'returned' keyword only accepts 'key' or 'value'.")


#        elif isinstance(iterable, list):
#            index = 0            

#            for el in iterable:

                #This part was added to catch lists of string values (guidelines, keywords)
#                if(returned == "value"):                
#                    if not (isinstance(el, dict) or isinstance(el, list)):
#                        strValue = ', '.join(iterable)
#                        yield strValue
#                        break
                #########        

#                for ret in self.iterate_all(el, returned=returned, prefix=str(index)):
#                    yield ret
#                index = index + 1















# Aqui ya genera ambos, key y value. 
#        if isinstance(iterable, dict):
#                for key, value in iterable.items():
#                    if returned == "key":
#                        yield key

#                        for ret in self.iterate_all(value, returned=returned):
#                            yield key + "[" +prefix+"]." + ret 


#                    elif returned == "value":
#                        if not (isinstance(value, dict) or isinstance(value, list)):
#                            yield value

#                        for ret in self.iterate_all(value, returned=returned):
#                            yield ret
#                    else:
#                        raise ValueError("'returned' keyword only accepts 'key' or 'value'.")

#        elif isinstance(iterable, list):
#            index = 0            

#            for el in iterable:
#                for ret in self.iterate_all(el, returned=returned, prefix=str(index)):
#                    yield ret
#                index = index + 1



# Con los primeros cambios. Funciona bien, pero solo genera keys
#        if isinstance(iterable, dict):
#            for key, value in iterable.items():
                
#                if not (isinstance(value, dict) or isinstance(value, list)):
#                    if((value in nullCards) or (value is None)):
#                        print("NULL VALUE ", value, " en ", key)
#                    yield key 
#                else:
#                    if(len(value) <1):
#                        print("NULL VALUE ", value, " en ", key)
#                        yield key 

#                for ret in self.iterate_all(value):
#                    yield key + "[" +prefix+"]." + ret 

#        elif isinstance(iterable, list):
#            index = 0            
#            for el in iterable:
#                for ret in self.iterate_all(el, str(index)):
#                    yield ret 
#                index = index + 1





# ORIGINAL
#        if isinstance(iterable, dict):
#                for key, value in iterable.items():
#                    if returned == "key":
#                        yield key
#                    elif returned == "value":
#                        if not (isinstance(value, dict) or isinstance(value, list)):
#                            yield value
#                    else:
#                        raise ValueError("'returned' keyword only accepts 'key' or 'value'.")
#                    for ret in self.iterate_all(value, returned=returned):
#                        yield ret
#        elif isinstance(iterable, list):
#            for el in iterable:
#                for ret in self.iterate_all(el, returned=returned):
#                    yield ret