from DQE.Rules.RulesTemplate import RuleTemplate

from collections import defaultdict, Counter

import pandas as pd
import numpy as np 
import ast
import re
import sys
import os


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

        self.create_list_from_dict(resultsFiltered, "target", dfScoringMatrix)
        self.create_list_from_dict(resultsFiltered, "crop", dfScoringMatrix)

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
        """Stored in resultsRaw and allFields the final value in the json input that does not contain any nested field
        
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
        """If CROPSAFETY is the only objective, then the target is not required
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 

        """


        if ('Objective' in resultsFiltered['general'][0]) & (resultsFiltered['general'][0]['Objective'] is not None):
            if(resultsFiltered['general'][0]['Objective'] == "CROPSAFETY"):
                resultsFiltered['general'][0]['target'] = "Not required"
                dfScoringMatrix.at['target','Weight'] = 0

#                del resultsFiltered['target'][:]
#                resultsFiltered['target'].append({'Target':'Not required'})

  





    def calculate_scores(self, resultsFiltered, dfScoringMatrix, allFields, tptIdKey):
        """Calculates the final scores taking into account Missing and Not required fields
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 
             - allFields: <dictionary> 
             - tptIdKey: <string> 
        """

        sections=list(dict.fromkeys((dfScoringMatrix.loc[dfScoringMatrix["Weight"]> 0]['Section'].values).tolist()))

        for key, value in resultsFiltered.items():

            totalFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key) & (dfScoringMatrix["Weight"]>0)].index.values.tolist()
            sectionFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key)].index.values.tolist()
            weightTotalFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key) & (dfScoringMatrix["Weight"]>0)]["Weight"].sum()

            sections.remove(key)
            indexItem =1


            for i in range(len(value)):     

#                addFields = list(set(sectionFields) - set(value[i]))

 #               for j in range(len(addFields)):     
  #                  if addFields[j] in totalFields:
   #                     value[i].update({addFields[j]:'Missing'})
    #                else:                
     #                   value[i].update({addFields[j]:'Not required'})


                presentFields = [kk for (kk, vv) in value[i].items() if ((vv != 'Missing') & (vv != 'Not required')) ]

                weightPresentFields = dfScoringMatrix[dfScoringMatrix.index.isin(presentFields)]["Weight"].sum()

                value[i].update({'rawScore':(len(list(set(totalFields).intersection(presentFields)))/len(totalFields))})
                value[i].update({'weightedScore':(weightPresentFields/weightTotalFields)})

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
        result = []

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
        
        result.append(missingFields)

        return result





    def create_list_from_dict(self, resultsFiltered, section, dfScoringMatrix):
        listResults = []
        results =""

        for item in resultsFiltered[section]:
            for k,v in item.items():
                listResults.append(v)

        if len(listResults)>0:
            results = ', '.join(listResults)
        else:
            results = "Missing"

        del resultsFiltered[section]
        resultsFiltered['general'][0].update({section:results})

        dfScoringMatrix.at[section,'Section'] = 'general'




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
            dfFiltered = df.loc[(df["Status"] == 0) & (df["Trial"] == trialType) & (df["Indication"] == indication)]


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





    # def _rule_definition(self, data, inputs, schema=None):

    #     tptIdKey = data["trialDescriptions"][0].pop("tptIdKey")
    #     weights = inputs.get('weights')
    #     version = inputs.get('version')
    #     attributeMapping = inputs.get('attributeMapping')
    #     indication= self.get_indication(tptIdKey) 
    #     trialType = self.get_trial_type(tptIdKey)


    #     dfScoringMatrix = self.read_rules(indication, trialType, weights) # scoring matrix
    #     fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

    #     allFields = {}


    #     #This part reads the JSON input and creates a flat list of input fields
    #     index = 0 
    #     for element in data["trialDescriptions"]:
    #         for item in element:
    #             if (isinstance(data["trialDescriptions"][index][item], list)):
    #                 self.check_list(data["trialDescriptions"][index][item], "trialDescriptions." + item, allFields)
    #             else:
    #                 self.last_item("trialDescriptions." + item, data["trialDescriptions"][index][item], allFields)

    #         index = index + 1       



    #     newFields = self.translate_fields(allFields, fieldMapping, dfScoringMatrix)

    #     newCrops = self.fields_to_string(newFields, "crop")
    #     newFields["general"]["Crop"]= newCrops
    #     newFields.pop('crop', None)
    #     dfScoringMatrix.at['Crop', 'Section'] = "general"

    #     newTargets = self.fields_to_string(newFields, "target")
    #     newFields["general"]["Target"]= newTargets
    #     newFields.pop('target', None)
    #     dfScoringMatrix.at['Target', 'Section'] = "general"


    #     allScores = self.calculate_scores(newFields, dfScoringMatrix)

    #     missingFields = self.missing_fields(newFields, dfScoringMatrix)



    #     return {
    #         self.name: {"input": allFields, "translatedInput":newFields, "missingFields": missingFields, "scores": allScores, "version": version
    #         }
    #     }




    # def translate_fields(self, allFields, fieldMapping, dfScoringMatrix):
    #     mydict = lambda: defaultdict(mydict)
    #     newFields = mydict()

    #     for key, value in allFields.items():
    #         keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

    #         if((keyNoIndex not in fieldMapping)):   # Fields not included in the attribute mapping file 
    #             print(keyNoIndex, " could not be found in the scoring matrix" )
    #             continue


    #         keyDF = fieldMapping[keyNoIndex]
    #         section = dfScoringMatrix.loc[[keyDF],['Section']].values[0][0]
    #         exception = dfScoringMatrix.loc[[keyDF],['Exception']].values[0][0]
    #         weight = int(dfScoringMatrix.loc[[keyDF],['Weight']].values[0][0])


    #         if(weight < 1):         # weights with a value of 0 indicated fields that are not required due to trial type or indication
    #             value= "Not required"

    #         if(pd.notna(exception)):    # If the objective has a value = "cropsafety" then the target is not required 
    #             if(self.exception_CROPSAFETY(allFields)):                                        
    #                 value= "Not required"


    #         if(value=='Missing'):       #Use the 'Missing' label instead of the null values
    #             value= "Missing"

    #         mainIndex = self.get_index(key, "mainIndex")            

    #         if(mainIndex is None):  #general section
    #             newFields[section][keyDF]=value
    #         else:
    #             newFields[section][mainIndex][keyDF]=value


    #     return newFields




    # def calculate_scores(self, newFields, dfScoringMatrix):
    #     """Returns raw and weighted scores for each section
        
    #     Arguments:
    #         - newFields: <dictionary> 
    #         - dfScoringMatrix: <dataframe> 

    #     Returns:
    #         - results: <dictionary>
    #     """


    #     mydict = lambda: defaultdict(mydict)
    #     results = mydict()
    #     weights = defaultdict(Counter)       
    #     counts = defaultdict(Counter)       
    #     hasException =False


    #     # Here the data in the dictionary is read an the keys looked in the dataframe to collect the weights 
    #     for k, v in newFields.items():
    #         for kk, vv in v.items():
    #             if(isinstance(vv, dict)):
    #                 for kkk, vvv in vv.items():
    #                     weight = int(dfScoringMatrix.loc[[kkk],['Weight']].values[0][0])

    #                     if(vvv != 'Missing'):
    #                         weights[k][kk] += weight          
    #                         counts[k][kk] += 1          
    #                     else:
    #                         weights[k][kk] += 0          
    #                         counts[k][kk] += 0          

    #             else:
    #                 if(vv == "Not required"):
    #                     hasException = True
    #                     continue

    #                 weight = int(dfScoringMatrix.loc[[kk],['Weight']].values[0][0])

    #                 if(vv != 'Missing'):
    #                     weights[k]['0'] += weight          
    #                     counts[k]['0'] += 1          
    #                 else:
    #                     weights[k]['0'] += 0          
    #                     counts[k]['0'] += 0          


    #     # the total counts and weights are calculated here so that the final score (count/totalCount) can be calculated 
    #     for k, v in weights.items():
    #         if(hasException):
    #             totalWeights = dfScoringMatrix[(dfScoringMatrix["Section"]==k) & (dfScoringMatrix["Exception"]!="CROPSAFETY")]["Weight"].sum()
    #             totalRows = dfScoringMatrix[(dfScoringMatrix["Section"]==k) & (dfScoringMatrix["Exception"]!="CROPSAFETY")]["Weight"].count()
    #         else:
    #             totalWeights = dfScoringMatrix[dfScoringMatrix["Section"]==k]["Weight"].sum()
    #             totalRows = dfScoringMatrix[dfScoringMatrix["Section"]==k]["Weight"].count()

    #         for kk, vv in v.items():
    #             results[k][kk]['raw']= counts[k][kk]/totalRows
    #             results[k][kk]['weighted']= vv/totalWeights


    #     return results


    # def check_list(self, ele, prefix, allFields):
    #     if (not ele):
    #         self.last_item(prefix, "Missing", allFields)
    #     elif not (isinstance(ele[0], dict) or isinstance(ele[0], list)):
    #         strValue = ', '.join(ele)
    #         self.last_item(prefix, strValue, allFields)
    #         return

    #     for i in range(len(ele)):
    #         if (isinstance(ele[i], list)):
    #             self.check_list(ele[i], prefix+"["+str(i)+"]", allFields)
    #         elif (isinstance(ele[i], dict)):
    #             self.check_dict(ele[i], prefix+"["+str(i)+"]", allFields)                
    #         else:
    #             self.last_item(prefix+"["+str(i)+"]", ele[i], allFields)



    # def check_dict(self, jsonObject, prefix, allFields):
    #     for ele in jsonObject:
    #         if (isinstance(jsonObject[ele], dict)):
    #             self.check_dict(jsonObject[ele], prefix+"."+ele, allFields)

    #         elif (isinstance(jsonObject[ele], list)):
    #             self.check_list(jsonObject[ele], prefix+"."+ele, allFields)

    #         else:
    #             self.last_item(prefix+"."+ele, jsonObject[ele], allFields)









    # def missing_fields(self, newFields, dfScoringMatrix):
    #     """Returns the fields missing in the input data
        
    #     Arguments:
    #         - newFields: <dictionary> 
    #         - dfScoringMatrix: <dataframe> 

    #     Returns:
    #         - results <dictionary>
    #     """


    #     results = {}
 
    #     keysDataFrame = list(dict.fromkeys(dfScoringMatrix['Section'].values))
    #     for x in keysDataFrame:
    #         if (x not in newFields.keys()) or (len(newFields[x]) <1):
    #             results[x]=(dfScoringMatrix.loc[dfScoringMatrix["Section"]== x].index.values).tolist()

    #     return results



    # def exception_CROPSAFETY(self, allFields):
    #     """Returns a boolean that indicates if the CROPSAFETY exception occurs.
            
    #     Arguments:
    #         - dictFinal: <dictionary> 

    #     Returns:
    #         - <Boolean>
    #     """

    #     try:
    #        objective = allFields['trialDescriptions.keywords']

    #        if objective.strip() == "CROPSAFETY":
    #            caseException = True
    #        else:
    #            caseException = False

    #     except pd.errors.EmptyDataError:
    #        caseException = False

    #     return caseException







    # def fields_to_string(self, newFields, section):
    #     """Returns a single string that contains all the values of a dictionary   
        
    #     Arguments:
    #         - newFields: <dictionary> 
    #         - section: <string> 

    #     Returns:
    #         - result <string>
    #     """

    #     result= ""
    #     for x in newFields[section].values():
    #         if(x != "Not required") & (x != "Missing"):
    #             for k,v in x.items():
    #                 if(v == "Not required"):
    #                     result = v
    #                 else:
    #                     result = result + str(v) + " - "
    #         else:
    #             result = x


    #     if not result:
    #         return "Missing"
    #     else:
    #         return result





    # def last_item(self, prefix, item, allFields):
    #     """Returns the final value in the json input that does not contain any nested field
        
    #     Arguments:
    #         - prefix: <string> 
    #         - item: <string> 
    #         - allFields: <dictionary> 

    #     """

    #     nullCards = ['*','.','?']

    #     if((item in nullCards) or (item is None) or (item is False)):
    #         allFields[str(prefix)]= 'Missing'
    #     else:
    #         allFields[str(prefix)]= item



    # def read_rules(self, indication, trialType, weights):
    #     """Returns a dataframe that contains the weights used to calculate the scores. 
    #     The dataframe is filtered to contain only the correspondant indication and trial type   
        
    #     Arguments:
    #         - indication: <string> 
    #         - trialType: <string> 
    #         - weights: <string> 

    #     Returns:
    #         - <dataframe>
    #     """
    #     try:
    #         dfWeights = os.path.join(weights)
    #         df = pd.read_csv(dfWeights, delimiter=",", index_col="Field", converters=None)
    #         dfFiltered = df.loc[(df["Status"] == 0) & (df["Trial"] == trialType) & (df["Indication"] == indication)]

    #     except pd.errors.EmptyDataError:
    #         dfFiltered = pd.DataFrame()

    #     except:
    #         raise ValueError("Unexpected error:", sys.exc_info()[0])
    #         return 1


    #     return dfFiltered



    # def get_indication(self, tptIdKey):
    #     """Returns the indication as defined in the tptIdKey
          
    #     Arguments:
    #         - tptIdKey: <string> 

    #     Returns:
    #         - <string>
    #     """

    #     indication = tptIdKey.strip()[0:1]

    #     if(indication not in ['I','F','H','S']):
    #         indication = 'II'

    #     return indication


    # def get_trial_type(self, tptIdKey):
    #     """Returns the trial type as defined in the tptIdKey

    #     Arguments:
    #         - tptIdKey: <string> 

    #     Returns:
    #         - <string>
    #     """

    #     trialType = tptIdKey.strip()[1:2]
    #     if(trialType not in ['A','R','D']):
    #         trialType = 'TT'

    #     return trialType




    # def read_file_mappings(self, path):
    #     """Returns the trial type as defined in the tptIdKey

    #     Arguments:
    #         - tptIdKey: <string> 

    #     Returns:
    #         - <string>
    #     """

    #     try:
    #         f = open(path, "r")
    #         contents = f.read()
    #         attributeMapping = ast.literal_eval(contents)

    #     except:
    #         raise ValueError("Unexpected error:", sys.exc_info()[0])
    #     return attributeMapping


    # def get_index(self, key, case):
    #     """Returns an integer index that is used to store the applications into separate key-value pairs
        
    #     Arguments:
    #         - key: <string> 
    #         - case: <string> 

    #     Returns:
    #         - indexes[] <integer>
    #     """



    #     indexes = re.findall(r'\d+', key)

    #     if(len(indexes)==0):
    #         return None

    #     if(case == 'subIndex'):
    #         if(len(indexes)>1):
    #             return indexes[1]
    #         else:
    #             return None
    #     elif(case == 'mainIndex'):
    #         return indexes[0]
    #     else:
    #         if(len(indexes)>2):
    #             return indexes[2]
    #         else:
    #             return None




