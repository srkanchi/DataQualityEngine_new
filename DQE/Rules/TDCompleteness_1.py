from DQE.Rules.RulesTemplate import RuleTemplate

from collections import defaultdict, Counter

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
        indication= self.get_indication(tptIdKey) 
        trialType = self.get_trial_type(tptIdKey)


        dfScoringMatrix = self.read_rules(indication, trialType, weights) # scoring matrix

        fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

        allFields = {}


        #This part reads the JSON input and creates a flat list of input fields
        index = 0 
        for element in data["trialDescriptions"]:
            for item in element:
                if (isinstance(data["trialDescriptions"][index][item], list)):
                    self.checkList(data["trialDescriptions"][index][item], "trialDescriptions." + item, allFields)
                else:
                    self.last_item("trialDescriptions." + item, data["trialDescriptions"][index][item], allFields)

            index = index + 1       





        # These variables are used to calculate the scores 
        mydict = lambda: defaultdict(mydict)
        newFields = mydict()
        weights = defaultdict(Counter)       
        counts = defaultdict(Counter)       
        totalWeights = defaultdict(Counter)       
        totalCounts = defaultdict(Counter)       

        applIndex = 0
        prevMainIndex = 0
        prevSubindex =0

        for key, value in allFields.items():
            keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

            if((keyNoIndex not in fieldMapping)):   # Fields not included in the attribute mapping file 
                print(keyNoIndex, " could not be found in the scoring matrix" )
                continue


            keyDF = fieldMapping[keyNoIndex]
            section = dfScoringMatrix.loc[[keyDF],['Section']].values[0][0]
            exception = dfScoringMatrix.loc[[keyDF],['Exception']].values[0][0]
            weight = int(dfScoringMatrix.loc[[keyDF],['Weight']].values[0][0])
            weightTotal = weight
            count = 1
            countTotal = count



            if(weight < 1):         # weights with a value of 0 indicated fields that are not required due to trial type or indication
                value= "Not required"
                weight=0
                weightTotal = 0
                countTotal = 0
                count = 0 



            if(pd.notna(exception)):    # If a standard evaluations starts with P or H some fields are not required
                if(self.exception_PHSES(key, value, allFields)==True):
                    value= "Not required"
                    weight=0
                    weightTotal = 0
                    countTotal = 0
                    count = 0 


            if(value=='Missing'):       #missing or null values
                weight = 0
                count = 0



            # More than one application may accur at a determined cropstage. This generates duplicated entries. The following code
            # separates these duplicated entries into dictionary value-key pairs, which makes easier the calculation of scores
            mainIndex = self.get_index(key, "mainIndex")            
            subIndex = self.get_index(key, "subIndex")


            if((mainIndex is not None) & (subIndex is not None)):
                if((mainIndex != prevMainIndex) or (subIndex != prevSubIndex)  ):
                    prevMainIndex = mainIndex
                    prevSubIndex = subIndex
                    applIndex = applIndex + 1

            if(mainIndex is None):
                newFields[section]['0'][keyDF]=value

                weights[section]['0'] += weight          
                counts[section]['0'] += count          
                totalWeights[section]['0'] += weightTotal          
                totalCounts[section]['0'] += countTotal          

            elif(subIndex is None):
                newFields[section][mainIndex][keyDF]=value

                weights[section][mainIndex] += weight          
                counts[section][mainIndex] += count          
                totalWeights[section][mainIndex] += weightTotal          
                totalCounts[section][mainIndex] += countTotal          

            else:
                newFields[section][applIndex][keyDF]=value

                weights[section][applIndex] += weight          
                counts[section][applIndex] += count          
                totalWeights[section][applIndex] += weightTotal          
                totalCounts[section][applIndex] += countTotal          




        filteredApplications = self.remove_duplicated_applications(newFields)
        newFields["applications"] = filteredApplications


        allScores = self.final_scores(weights, counts, totalWeights, totalCounts, filteredApplications)





        return {
            self.name: {"input": newFields, "scores": allScores, "version": version
            }
        }




    def checkList(self, ele, prefix, allFields):

        if (not ele):
            self.last_item(prefix, "Missing", allFields)
        for i in range(len(ele)):
            if (isinstance(ele[i], list)):
                self.checkList(ele[i], prefix+"["+str(i)+"]", allFields)
            elif (isinstance(ele[i], dict)):
                self.checkDict(ele[i], prefix+"["+str(i)+"]", allFields)                
            else:
                self.last_item(prefix+"["+str(i)+"]", ele[i], allFields)


    def checkDict(self, jsonObject, prefix, allFields):
        for ele in jsonObject:
            if (isinstance(jsonObject[ele], dict)):
                self.checkDict(jsonObject[ele], prefix+"."+ele, allFields)

            elif (isinstance(jsonObject[ele], list)):
                self.checkList(jsonObject[ele], prefix+"."+ele, allFields)

            else:
                self.last_item(prefix+"."+ele, jsonObject[ele], allFields)





    def remove_duplicated_applications(self, newFields):
        """Returns a dictionary that contains non duplicated applications   
        
        Arguments:
            - newFields: <dictionary> 

        Returns:
            - result <dictionary>
        """

        result = {}
        
        for key, value in newFields["applications"].items():
            if value not in result.values():
                result[key] = value

        return result







    def final_scores(self, weights, counts, totalWeights, totalCounts, filteredApplications):
        """Returns a dictionary that contains raw and weighted scores for each section:general, applications and assessments   
        
        Arguments:
            - weights: <Counter> 
            - counts: <Counter> 
            - totalWeights: <Counter> 
            - totalCounts: <Counter> 
            - filteredApplications: <dictionary>

        Returns:
            - result <dictionary>
        """

        mydict = lambda: defaultdict(mydict)
        results = mydict()

        for key, value in weights.items():
            for kk, vv in value.items():
                if((counts[key][kk] > 0) & (vv > 0)):
                    results[key][kk]["raw"] = counts[key][kk] / totalCounts[key][kk]
                    results[key][kk]["weighted"] = vv / totalWeights[key][kk]
                else:
                   results[key][kk]["raw"] = 0
                   results[key][kk]["weighted"] = 0


    #This following part is used to removed scores from duplicated applications 
        applicationKeys= results["applications"].keys()
        keysToRemove = []
        for key in results["applications"].keys():
            if not key in filteredApplications:
                keysToRemove.append(key)

        for k in keysToRemove:
            results["applications"].pop(k, None)


        return results


    def get_index(self, key, case):
        """Returns an integer index that is used to store the applications into separate key-value pairs
        
        Arguments:
            - key: <string> 
            - case: <string> 

        Returns:
            - indexes[] <integer>
        """



        indexes = re.findall(r'\d+', key)

        if(len(indexes)==0):
            return None

        if(case == 'subIndex'):
            if(len(indexes)>1):
                return indexes[1]
            else:
                return None
        else:
            return indexes[0]




    def exception_PHSES(self, key, value, allFields):
        """Returns a boolean to indicate if the exception is applicable
        
        Arguments:
            - key: <string> 
            - value: <string> 
            - allFields: <dictionary> 

        Returns:
            - <boolean>
        """

        pathSE = ".".join(key.split(".", 2)[:2])
        pathSE = pathSE + ".standardEvaluationId"

        SE = (allFields[pathSE]).strip()[0:1]

        if(SE != value):
            if((SE == "P") or(SE == "H")):
                return True
            else:
                return False
        else:
            return False




    def last_item(self, prefix, item, allFields):
        """Returns the final value in the json input that does not contain any nested field
        
        Arguments:
            - prefix: <string> 
            - item: <string> 
            - allFields: <dictionary> 

        """

        nullCards = ['*','.','?']

        if((item in nullCards) or (item is None)):
            allFields[str(prefix)]= 'Missing'
        else:
            allFields[str(prefix)]= item



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




