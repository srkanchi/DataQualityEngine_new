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
#        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#            print(dfScoringMatrix)

        fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

        allFields = {}
        resultsFinal = {}

        mydict = lambda: defaultdict(mydict)
        resultsRaw = mydict()


        index = 0 
        for element in data["trialDescriptions"]:
            for item in element:
                if (isinstance(data["trialDescriptions"][index][item], list)):
                    self.check_list(data["trialDescriptions"][index][item], "trialDescriptions." + item, fieldMapping, dfScoringMatrix, resultsRaw, allFields)
                elif (isinstance(data["trialDescriptions"][index][item], dict)):
                    self.check_dict(data["trialDescriptions"][index][item], "trialDescriptions." + item,  fieldMapping, dfScoringMatrix, resultsRaw, allFields)
                else:
                    self.last_item("trialDescriptions." + item, data["trialDescriptions"][index][item],  fieldMapping, dfScoringMatrix, resultsRaw, allFields)
            index = index + 1       


        resultsFiltered = self.remove_duplicates(resultsRaw)

        self.find_exceptions(resultsFiltered, dfScoringMatrix)
        self.calculate_scores(resultsFiltered, dfScoringMatrix, allFields, tptIdKey)

        return {
                self.name: {"input": allFields, "translatedInput": resultsFiltered, "version": version
             }
        }




    def check_list(self, ele, prefix, fieldMapping, dfScoringMatrix, resultsRaw, allFields):
        if (not ele):
            self.last_item(prefix, "Missing", fieldMapping, dfScoringMatrix, resultsRaw, allFields)
        elif not (isinstance(ele[0], dict) or isinstance(ele[0], list)):
            strValue = ', '.join(ele)
            self.last_item(prefix, strValue, fieldMapping, dfScoringMatrix, resultsRaw, allFields)
            return

        for i in range(len(ele)):     
            if (isinstance(ele[i], dict)):
                self.check_dict(ele[i], prefix+"["+str(i)+"]", fieldMapping, dfScoringMatrix, resultsRaw, allFields)
            else:
                self.last_item(prefix+"["+str(i)+"]", ele[i], allFields, dfScoringMatrix, resultsRaw, allFields)



    def check_dict(self, jsonObject, prefix, fieldMapping, dfScoringMatrix, resultsRaw, allFields):

        for ele in jsonObject:
            if (isinstance(jsonObject[ele], dict)):
                self.check_dict(jsonObject[ele], prefix+"."+ele, fieldMapping,dfScoringMatrix, resultsRaw, allFields)
            elif (isinstance(jsonObject[ele], list)):
                self.check_list(jsonObject[ele], prefix+"."+ele, fieldMapping, dfScoringMatrix, resultsRaw, allFields)

            else:
                self.last_item(prefix+"."+ele, jsonObject[ele],  fieldMapping, dfScoringMatrix, resultsRaw, allFields)







    def last_item(self, prefix, item, fieldMapping, dfScoringMatrix, resultsRaw, allFields):
        """Returns the final value in the json input that does not contain any nested field
        
        Arguments:
             - prefix: <string> 
             - item: <string> 
             - allFields: <dictionary> 

        """
        results = {}
        nullCards = ['*','.','?']
        translatedKey = self.get_field_name(fieldMapping, prefix)

        if translatedKey is None:
            return

        section = dfScoringMatrix.loc[[translatedKey],['Section']].values[0][0]
        weight = dfScoringMatrix.loc[[translatedKey],['Weight']].values[0][0]


        allFields[prefix]=item

        if(weight == 0):
            item= 'Not required'

        elif((item in nullCards) or (item is None) or (item is False)):
            item= 'Missing'


        subIndex = self.get_index(prefix, "subIndex")
        mainIndex = self.get_index(prefix, "mainIndex")

        if subIndex is None:
            resultsRaw[section][mainIndex][0][translatedKey]= str(item) 
        else:
            resultsRaw[section][mainIndex][subIndex][translatedKey]= str(item) 




    def remove_duplicates(self, resultsRaw):
        """Returns a dictionary that contains non duplicated applications   
        
        Arguments:
            - newFields: <dictionary> 

        Returns:
            - result <dictionary>
        """

        result = {}

        for key, value in resultsRaw.items():
            listValues = []
            for k, v in value.items(): 
               for kk, vv in v.items():
                   listValues.append(dict(vv))

            result[key] = [i for n, i in enumerate(listValues) if i not in listValues[n + 1:]]

        return result


    def find_exceptions(self, resultsFiltered, dfScoringMatrix):
        """If the standard evaluation starts with either 'H' or 'P' then the target, crop and part rated are not needed
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 

        """

        if ("assessments" in resultsFiltered):
            for i in range(len(resultsFiltered['assessments'])):     
                SE = (resultsFiltered['assessments'][i]['Assessment table/Standard Evaluation (SE)']).strip()[0:1]

                if((SE == "P") or(SE == "H")):
                    resultsFiltered['assessments'][i]['Assessment table/Crop']= 'Not required'
                    resultsFiltered['assessments'][i]['Assessment table/Target']= 'Not required'
                    resultsFiltered['assessments'][i]['Assessment table/Part rated']= 'Not required'






    def calculate_scores(self, resultsFiltered, dfScoringMatrix, allFields, tptIdKey):

        """Calculates the final scores taking into account Missing and Not required fields
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 
             - allFields: <dictionary> 
             - tptIdKey: <string> 
        """

        sections=list(dict.fromkeys((dfScoringMatrix['Section'].values).tolist()))  
#        sections=list(dict.fromkeys((dfScoringMatrix.loc[dfScoringMatrix["Weight"]> 0]['Section'].values).tolist()))      


        for key, value in resultsFiltered.items():
            sections.remove(key)
            indexItem =1
            for i in range(len(value)):     

                presentFields = [kk for (kk, vv) in value[i].items() if ((vv != 'Missing') & (vv != 'Not required')) ]
                totalButNotRequiredFields = [kk for (kk, vv) in value[i].items() if ((vv != 'Not required')) ]

                weightPresentFields = dfScoringMatrix[dfScoringMatrix.index.isin(presentFields)]["Weight"].sum()
                weightTotalFields = dfScoringMatrix[dfScoringMatrix.index.isin(totalButNotRequiredFields)]["Weight"].sum()

                value[i].update({'weightedScore':(weightPresentFields/weightTotalFields)})
                value[i].update({'rawScore':(len(presentFields)/len(totalButNotRequiredFields))})
                value[i].update({key + ' number':indexItem})
                value[i].update({"trial number":tptIdKey})
                indexItem = indexItem  + 1 

        for i in range(len(sections)):     
            resultsFiltered[sections[i]]= self.missing_sections(sections[i], dfScoringMatrix, tptIdKey)



    def missing_sections(self, section, dfScoringMatrix, tptIdKey):
        """Adds all of the missing fields if a complete section is missing
        
        Arguments:
             - section: <string> 
             - dfScoringMatrix: <dictionary> 
             - tptIdKey: <string> 
        """

        missingFields = {}
        requiredFields = dfScoringMatrix[dfScoringMatrix['Section']==section]

        for index, row in requiredFields.iterrows():
             if row['Weight'] == 0:
                 missingFields.update({index:'Not required'})
             else:
                 missingFields.update({index:'Missing'})

        missingFields.update({'rawScore':'0'})
        missingFields.update({'weightedScore':'0'})
        missingFields.update({'trial number':tptIdKey})
        missingFields.update({section + ' number':1})
        
        return missingFields




    def get_index(self, prefix, case):
        """Returns an integer index that is used to store the applications into separate key-value pairs
        
        Arguments:
            - key: <string> 
            - case: <string> 

        Returns:
            - indexes[] <integer>
        """

        indexes = re.findall(r'\d+', prefix)

        if case == "mainIndex":
            if(len(indexes)==0):
                return 0
            else:
                return indexes[0]

        elif(len(indexes)<2):
            return None
        else:
            return indexes[1]





    def get_field_name(self, fieldMapping, key):
        keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

        if((keyNoIndex not in fieldMapping)):   # Fields not included in the attribute mapping file 
            return None
        else:
            return fieldMapping[keyNoIndex]



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
#            dfFiltered = df.loc[(df["Trial"] == trialType) & (df["Indication"] == indication)]
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





#     def _rule_definition(self, data, inputs, schema=None):

#         tptIdKey = data["trialDescriptions"][0].pop("tptIdKey")
#         weights = inputs.get('weights')
#         version = inputs.get('version')
#         attributeMapping = inputs.get('attributeMapping')
#         indication= self.get_indication(tptIdKey) 
#         trialType = self.get_trial_type(tptIdKey)


#         dfScoringMatrix = self.read_rules(indication, trialType, weights) # scoring matrix
# #        pprint.pprint(dfScoringMatrix)
#         fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

#         allFields = {}


#         #This part reads the JSON input and creates a flat list of input fields
#         index = 0 
#         for element in data["trialDescriptions"]:
#             for item in element:
#                 if (isinstance(data["trialDescriptions"][index][item], list)):
#                     self.check_list(data["trialDescriptions"][index][item], "trialDescriptions." + item, allFields)
#                 else:
#                     self.last_item("trialDescriptions." + item, data["trialDescriptions"][index][item], allFields)

#             index = index + 1       





#         # These variables are used to calculate the scores 
#         mydict = lambda: defaultdict(mydict)
#         newFields = mydict()
#         weights = defaultdict(Counter)       
#         counts = defaultdict(Counter)       
#         totalWeights = defaultdict(Counter)       
#         totalCounts = defaultdict(Counter)       

#         applIndex = 0
#         prevMainIndex = 0
#         prevSubindex =0

#         for key, value in allFields.items():
#             keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

#             if((keyNoIndex not in fieldMapping)):   # Fields not included in the attribute mapping file 
#                 print(keyNoIndex, " could not be found in the scoring matrix" )
#                 continue


#             keyDF = fieldMapping[keyNoIndex]
#             section = dfScoringMatrix.loc[[keyDF],['Section']].values[0][0]
#             exception = dfScoringMatrix.loc[[keyDF],['Exception']].values[0][0]
#             weight = int(dfScoringMatrix.loc[[keyDF],['Weight']].values[0][0])
#             weightTotal = weight
#             count = 1
#             countTotal = count



#             if(weight < 1):         # weights with a value of 0 indicated fields that are not required due to trial type or indication
#                 value= "Not required"
#                 weight=0
#                 weightTotal = 0
#                 countTotal = 0
#                 count = 0 



#             if(pd.notna(exception)):    # If a standard evaluations starts with P or H some fields are not required
#                 if(self.exception_PHSES(key, value, allFields)==True):
#                     value= "Not required"
#                     weight=0
#                     weightTotal = 0
#                     countTotal = 0
#                     count = 0 


#             if(value=='Missing'):       #missing or null values
#                 weight = 0
#                 count = 0



#             # More than one application may accur at a determined cropstage. This generates duplicated entries. The following code
#             # separates these duplicated entries into dictionary value-key pairs, which makes easier the calculation of scores
#             mainIndex = self.get_index(key, "mainIndex")            
#             subIndex = self.get_index(key, "subIndex")


#             if((mainIndex is not None) & (subIndex is not None)):
#                 if((mainIndex != prevMainIndex) or (subIndex != prevSubIndex)  ):
#                     prevMainIndex = mainIndex
#                     prevSubIndex = subIndex
#                     applIndex = applIndex + 1

#             if(mainIndex is None):  #general
#                 newFields[section]['0'][keyDF]=value

#                 weights[section]['0'] += weight          
#                 counts[section]['0'] += count          
#                 totalWeights[section]['0'] += weightTotal          
#                 totalCounts[section]['0'] += countTotal          

#             elif(subIndex is None): # Assessments
#                 newFields[section][mainIndex][keyDF]=value

#                 weights[section][mainIndex] += weight          
#                 counts[section][mainIndex] += count          
#                 totalWeights[section][mainIndex] += weightTotal          
#                 totalCounts[section][mainIndex] += countTotal          

#             else: # applications
#                 thirdIndex = self.get_index(key, "thirdIndex")

#                 if((thirdIndex is None) or (thirdIndex == "0")):

#                     newFields[section][applIndex][keyDF]=value

#                     weights[section][applIndex] += weight          
#                     counts[section][applIndex] += count          
#                     totalWeights[section][applIndex] += weightTotal          
#                     totalCounts[section][applIndex] += countTotal          


#         filteredApplications = self.remove_duplicated_applications(newFields)
#         newFields["applications"] = filteredApplications

#         allScores = self.final_scores(weights, counts, totalWeights, totalCounts, filteredApplications)

#         missingFields = self.missing_fields(newFields, dfScoringMatrix)


#         return {
#             self.name: {"input": allFields, "translatedInput":newFields, "missingFields": missingFields, "scores": allScores, "version": version
#             }
#         }




#     def check_list(self, ele, prefix, allFields):
#         if (not ele):
#             self.last_item(prefix, "Missing", allFields)
#         elif not (isinstance(ele[0], dict) or isinstance(ele[0], list)):
#             strValue = ', '.join(ele)
#             self.last_item(prefix, strValue, allFields)
#             return

#         for i in range(len(ele)):
#             if (isinstance(ele[i], list)):
#                 self.check_list(ele[i], prefix+"["+str(i)+"]", allFields)
#             elif (isinstance(ele[i], dict)):
#                 self.check_dict(ele[i], prefix+"["+str(i)+"]", allFields)                
#             else:
#                 self.last_item(prefix+"["+str(i)+"]", ele[i], allFields)



#     def check_dict(self, jsonObject, prefix, allFields):
#         for ele in jsonObject:
#             if (isinstance(jsonObject[ele], dict)):
#                 self.check_dict(jsonObject[ele], prefix+"."+ele, allFields)

#             elif (isinstance(jsonObject[ele], list)):
#                 self.check_list(jsonObject[ele], prefix+"."+ele, allFields)

#             else:
#                 self.last_item(prefix+"."+ele, jsonObject[ele], allFields)





#     def remove_duplicated_applications(self, newFields):
#         """Returns a dictionary that contains non duplicated applications   
        
#         Arguments:
#             - newFields: <dictionary> 

#         Returns:
#             - result <dictionary>
#         """

#         result = {}
        
#         for key, value in newFields["applications"].items():
#             if value not in result.values():
#                 result[key] = value

#         return result







#     def final_scores(self, weights, counts, totalWeights, totalCounts, filteredApplications):
#         """Returns a dictionary that contains raw and weighted scores for each section:general, applications and assessments   
        
#         Arguments:
#             - weights: <Counter> 
#             - counts: <Counter> 
#             - totalWeights: <Counter> 
#             - totalCounts: <Counter> 
#             - filteredApplications: <dictionary>

#         Returns:
#             - result <dictionary>
#         """

#         mydict = lambda: defaultdict(mydict)
#         results = mydict()

#         for key, value in weights.items():
#             for kk, vv in value.items():
#                 if((counts[key][kk] > 0) & (vv > 0)):
#                     results[key][kk]["raw"] = counts[key][kk] / totalCounts[key][kk]
#                     results[key][kk]["weighted"] = vv / totalWeights[key][kk]
#                 else:
#                    results[key][kk]["raw"] = 0
#                    results[key][kk]["weighted"] = 0


#     #This following part is used to removed scores from duplicated applications 
#         applicationKeys= results["applications"].keys()
#         keysToRemove = []
#         for key in results["applications"].keys():
#             if not key in filteredApplications:
#                 keysToRemove.append(key)

#         for k in keysToRemove:
#             results["applications"].pop(k, None)


#         return results




#     def missing_fields(self, newFields, dfScoringMatrix):
#         """Returns the fields missing in the input data
        
#         Arguments:
#             - newFields: <dictionary> 
#             - dfScoringMatrix: <dataframe> 

#         Returns:
#             - results <dictionary>
#         """


#         results = {}
 
#         keysDataFrame = list(dict.fromkeys(dfScoringMatrix['Section'].values))
#         for x in keysDataFrame:
#             if (x not in newFields.keys()) or (len(newFields[x]) <1):
#                 results[x]=(dfScoringMatrix.loc[dfScoringMatrix["Section"]== x].index.values).tolist()

#         return results


#     def get_index(self, key, case):
#         """Returns an integer index that is used to store the applications into separate key-value pairs
        
#         Arguments:
#             - key: <string> 
#             - case: <string> 

#         Returns:
#             - indexes[] <integer>
#         """



#         indexes = re.findall(r'\d+', key)

#         if(len(indexes)==0):
#             return None

#         if(case == 'subIndex'):
#             if(len(indexes)>1):
#                 return indexes[1]
#             else:
#                 return None
#         elif(case == 'mainIndex'):
#             return indexes[0]
#         else:
#             if(len(indexes)>2):
#                 return indexes[2]
#             else:
#                 return None




#     def exception_PHSES(self, key, value, allFields):
#         """Returns a boolean to indicate if the exception is applicable
        
#         Arguments:
#             - key: <string> 
#             - value: <string> 
#             - allFields: <dictionary> 

#         Returns:
#             - <boolean>
#         """

#         pathSE = ".".join(key.split(".", 2)[:2])
#         pathSE = pathSE + ".standardEvaluationId"

#         SE = (allFields[pathSE]).strip()[0:1]

#         if(SE != value):
#             if((SE == "P") or(SE == "H")):
#                 return True
#             else:
#                 return False
#         else:
#             return False




#     def last_item(self, prefix, item, allFields):
#         """Returns the final value in the json input that does not contain any nested field
        
#         Arguments:
#             - prefix: <string> 
#             - item: <string> 
#             - allFields: <dictionary> 

#         """

#         nullCards = ['*','.','?']

#         if((item in nullCards) or (item is None)):
#             allFields[str(prefix)]= 'Missing'
#         else:
#             allFields[str(prefix)]= item



#     def read_rules(self, indication, trialType, weights):
#         """Returns a dataframe that contains the weights used to calculate the scores. 
#         The dataframe is filtered to contain only the correspondant indication and trial type   
        
#         Arguments:
#             - indication: <string> 
#             - trialType: <string> 
#             - weights: <string> 

#         Returns:
#             - <dataframe>
#         """
#         try:
#             dfWeights = os.path.join(weights)
#             df = pd.read_csv(dfWeights, delimiter=",", index_col="Field", converters=None)
#             dfFiltered = df.loc[(df["Status"] == 1) & (df["Trial"] == trialType) & (df["Indication"] == indication)]

#         except pd.errors.EmptyDataError:
#             dfFiltered = pd.DataFrame()

#         except:
#             raise ValueError("Unexpected error:", sys.exc_info()[0])
#             return 1


#         return dfFiltered



#     def get_indication(self, tptIdKey):
#         """Returns the indication as defined in the tptIdKey
          
#         Arguments:
#             - tptIdKey: <string> 

#         Returns:
#             - <string>
#         """

#         indication = tptIdKey.strip()[0:1]

#         if(indication not in ['I','F','H','S']):
#             indication = 'II'

#         return indication


#     def get_trial_type(self, tptIdKey):
#         """Returns the trial type as defined in the tptIdKey

#         Arguments:
#             - tptIdKey: <string> 

#         Returns:
#             - <string>
#         """

#         trialType = tptIdKey.strip()[1:2]
#         if(trialType not in ['A','R','D']):
#             trialType = 'TT'

#         return trialType




#     def read_file_mappings(self, path):
#         """Returns the trial type as defined in the tptIdKey

#         Arguments:
#             - tptIdKey: <string> 

#         Returns:
#             - <string>
#         """

#         try:
#             f = open(path, "r")
#             contents = f.read()
#             attributeMapping = ast.literal_eval(contents)

#         except:
#             raise ValueError("Unexpected error:", sys.exc_info()[0])
#         return attributeMapping




