

from DQE.Rules.RulesTemplate import RuleTemplate

import pandas as pd
import numpy as np 
import ast
import re
import sys
import os

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
        pprint.pprint(dictFinal)


        df = self.read_rules(indication, trialType, weights)
        pprint.pprint(df)


#        scores = self.calculate_scores(dictFinal, df, indication, trialType, attributeMapping)


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
        """Returns a boolean which indicates if the value contains nested values 
        
        Arguments:
            - value: <string> 
            
        Returns:
            - <Boolean>
        """

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




    def read_rules(self, indication, trialType, weights):
        """Returns a dataframe that contains the weights used to calculate the scores. 
        The dataframe is filtered to contain only the correspondant indication and trial type   
        
        Arguments:
            - indication: <string> 
            - trialType: <string> 
            - weights: <string> 

        Returns:
            - <dataframe>
        """
        try:
            dfWeights = os.path.join(weights)
            df = pd.read_csv(dfWeights, delimiter=",", index_col="Field", converters=None)
            dfFiltered = df.loc[(df["Status"] == 1) & (df["Trial"] == trialType) & (df["Indication"] == indication)]

        except pd.errors.EmptyDataError:
            dfFiltered = pd.DataFrame()

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])
            return 1


        return dfFiltered








    def calculate_scores(self, dictFinal, dfRules, indication, trialType, attributeMapping):

        fieldMapping = self.read_file_mappings(attributeMapping)
        default_totals= self.calculate_default_totals(dfRules)

        fields = dfRules.index.values

        totals = {"assessments":0, "general":0, "applications":0}
        counts = {"assessments":0, "general":0, "applications":0}
        totalsMissing = {"assessments":0, "general":0, "applications":0}
        countsMissing = {"assessments":0, "general":0, "applications":0}

        missingFields= []

 
        for key, value in dictFinal.items():
            keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

            if((keyNoIndex not in fieldMapping)):
                print(keyNoIndex, " could not be found in the scoring matrix" )
                continue

            keyDF = fieldMapping[keyNoIndex]
            section = dfRules.loc[[keyDF],['Section']].values[0][0]
            exception = dfRules.loc[[keyDF],['Exception']].values[0][0]
            weight = dfRules.loc[[keyDF],['Weight']].values[0][0]


            if(pd.notna(exception)):
                if(self.exception_PHSES(key, value, dictFinal)==True):
                    continue


            if(value=='Missing'):
                totalsMissing[section] = totalsMissing[section] + 1 
                countsMissing[section] = countsMissing[section] + int(weight)
#                missingFields.append(keyDF)
                continue


            totals[section]= totals[section] + int(weight)
            counts[section] = counts[section] + 1


            finalScores= self.calculate_final_scores(totals, counts, totalsMissing, countsMissing, default_totals)


        


        print("counts ", counts)
        print("total ", totals)
        print("totalsMissing ", totalsMissing)
        print("countsMissing ", countsMissing)
#        print("fieldazos ", fields)

        return False





    def calculate_final_scores(self, totals, counts, totalsMissing, countsMissing, default_totals):
        scores={"generalRaw":0, "assessmentsRaw":0, "applicationsRaw":0, "generalWeight":0, "assessmentsWeight":0, "applicationsWeight":0}
#        scores["generalRaw"] = (totals["general"] / (totals["general"] + totalsMissing["general"]) )

#        if(default_totals["assessments"] > counts["assessments"]):
#            print("mayor")
#        else:
#            scores["assessmentsRaw"] = (totals["assessments"] / (totals["assessments"] + totalsMissing["assessments"]) )
        print("--RAW--> ", self.compare_totals("assessments", default_totals, totals, totalsMissing, "raw" ))
        print("--WEIGHT--> ", self.compare_totals("assessments", default_totals, counts, countsMissing, "weighted"))



        return scores


    def compare_totals(self, section, default, totals, missing, typeScore):

        if(default[section] > totals[section]):
            print("mayor")
        else:
            score = (totals[section] / (totals[section] + totalsMissing[section]) )


        return True



    def exception_PHSES(self, key, value, dictFinal):
        pathSE = ".".join(key.split(".", 2)[:2])
#        pathSE = pathSE + ".standardEvaluationId"

        pathSE = pathSE + ".standardEvaluationId[" + re.findall(r'\d+', key)[-1] +"]"

        SE = (dictFinal[pathSE]).strip()[0:1]

        if(SE != value):
            if((SE == "P") or(SE == "H")):
                return True
            else:
                return False
        else:
            return False




    def get_indication(self, tptIdKey):
        """Returns the indication as defined in the tptIdKey
          
        Arguments:
            - tptIdKey: <string> 

        Returns:
            - <string>
        """

        indication = tptIdKey.strip()[0:1]

        if(indication not in ['I','F','H','S']):
            indication = 'II'

        return indication




    def calculate_default_totals(self, dfRules):
        totals = {"applications":0, "assessments":0}
        totals["applications"] = dfRules[dfRules["Section"]=="applications"]["Weight"].sum()
        totals["assessments"] = dfRules[dfRules["Section"]=="assessments"]["Weight"].sum()

        return totals





    def get_trial_type(self, tptIdKey):
        """Returns the trial type as defined in the tptIdKey

        Arguments:
            - tptIdKey: <string> 

        Returns:
            - <string>
        """

        trialType = tptIdKey.strip()[1:2]
        if(trialType not in ['A','R','D']):
            trialType = 'TT'

        return trialType




    def read_file_mappings(self, path):
        """Returns the trial type as defined in the tptIdKey

        Arguments:
            - tptIdKey: <string> 

        Returns:
            - <string>
        """

        try:
            f = open(path, "r")
            contents = f.read()
            attributeMapping = ast.literal_eval(contents)

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])
        return attributeMapping




