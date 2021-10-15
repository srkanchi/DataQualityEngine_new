from DQE.Rules.RulesTemplate import RuleTemplate

from collections import defaultdict, Counter

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

        tptIdKey = data["fieldtrials"][0].pop("tptIdKey")
        weights = inputs.get('weights')
        version = inputs.get('version')
        attributeMapping = inputs.get('attributeMapping')
        indication= self.get_indication(tptIdKey) 
        trialType = self.get_trial_type(tptIdKey)


        dfScoringMatrix = self.read_rules(indication, trialType, weights) # scoring matrix
        fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

        allFields = {}
        resultsFinal = {}
#        resultsFiltered = {}

        mydict = lambda: defaultdict(mydict)
        resultsRaw = mydict()


        index = 0 
        for element in data["fieldtrials"]:
            for item in element:
                if (isinstance(data["fieldtrials"][index][item], list)):
                    self.check_list(data["fieldtrials"][index][item], "fieldtrials." + item, fieldMapping, dfScoringMatrix, resultsRaw, allFields)
                elif (isinstance(data["fieldtrials"][index][item], dict)):
                    self.check_dict(data["fieldtrials"][index][item], "fieldtrials." + item,  fieldMapping, dfScoringMatrix, resultsRaw, allFields)
                else:
                    self.last_item("fieldtrials." + item, data["fieldtrials"][index][item],  fieldMapping, dfScoringMatrix, resultsRaw, allFields)
            index = index + 1       



        resultsFiltered = self.remove_duplicates(resultsRaw)

#        self.find_exceptions(resultsFiltered, dfScoringMatrix)
        self.calculate_scores(resultsFiltered, dfScoringMatrix, allFields, tptIdKey)

        return {
                self.name: {"input": resultsFiltered, "version": version #, "scores":allScores#"input": allFields, "translatedInput":newFields , "scores": allScores, "version": version
            }
        }





    def check_list(self, ele, prefix, fieldMapping, dfScoringMatrix, resultsRaw, allFields):

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
        section= self.get_field_section(fieldMapping, dfScoringMatrix, translatedKey)


        subIndex = self.get_index(prefix, "subIndex")
        mainIndex = self.get_index(prefix, "mainIndex")

        if((item in nullCards) or (item is None) or (item is False)):
            item= 'Missing'

        if subIndex is None:
            resultsRaw[section][mainIndex][0][translatedKey]= str(item) 
        else:
            resultsRaw[section][mainIndex][subIndex][translatedKey]= str(item) 

        allFields[prefix]=item




    def find_exceptions(self, resultsFiltered, dfScoringMatrix):

        fieldExceptions = dfScoringMatrix[(~dfScoringMatrix['Exception'].isnull()) & (dfScoringMatrix['Required']==1)]

        for index, row in fieldExceptions.iterrows():
            if row['Exception'] == "APPMETHOD":
                self.exception_APPMETHOD(index, row['Section'], resultsFiltered)
            elif row['Exception'] == "SEEDEXC":
                self.exception_SEEDEXC(index, row['Section'], resultsFiltered)

#            print(index,row['Exception'], row['Section'])



    def calculate_scores(self, resultsFiltered, dfScoringMatrix, allFields, tptIdKey):

        sections=list(dict.fromkeys((dfScoringMatrix.loc[dfScoringMatrix["Required"]== 1]['Section'].values).tolist()))


        for key, value in resultsFiltered.items():

            totalFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key) & (dfScoringMatrix["Required"]==1)].index.values.tolist()
            sections.remove(key)
            indexItem =1
            for i in range(len(value)):     

                presentFields = [kk for (kk, vv) in value[i].items() if vv != 'Missing' ]
                value[i].update({'score':(len(list(set(totalFields).intersection(presentFields)))/len(totalFields))})
                value[i].update({key + ' number':indexItem})
                value[i].update({"trial number":tptIdKey})
                indexItem = indexItem  + 1 


        for i in range(len(sections)):     
            resultsFiltered[sections[i]]= self.missing_sections(sections[i], dfScoringMatrix, tptIdKey)

        # if(len(sections)>0):
        #     resultsFinal[key]= self.missing_sections(sections, dfScoringMatrix)





    # def format_results(self, resultsRaw, translatedFields, dfScoringMatrix):

    #     sections=list(dict.fromkeys((dfScoringMatrix.loc[dfScoringMatrix["Required"]== 1]['Section'].values).tolist()))

    #     results= {}
    #     resultsMissing= {}

    #     for key, value in resultsRaw.items():
    #         results = []
    #         totalFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key) & (dfScoringMatrix["Required"]==1)].index.values.tolist()
    #         sections.remove(key)
    #         for k, v in value.items():
    #             presentFields = [kk for (kk, vv) in v.items() if vv != 'Missing' ]
    #             v.update({'score':(len(list(set(totalFields).intersection(presentFields)))/len(totalFields))})
    #             results.append(v)

    #         translatedFields[key]= results


    #     if(len(sections)>0):
    #         resultsMissing = self.missing_sections(sections, translatedFields, dfScoringMatrix)

    #     return resultsMissing


    def missing_sections(self, section, dfScoringMatrix, tptIdKey):

        missingFields = {}
        sectionFields = list(dict.fromkeys((dfScoringMatrix.loc[(dfScoringMatrix["Required"]== 1) & (dfScoringMatrix["Section"]==section)].index.values).tolist()))

        for j in range(len(sectionFields)):     
            missingFields.update({sectionFields[j]:'Missing'})
        missingFields.update({'score':'0'})
        missingFields.update({'trial number':tptIdKey})

        return missingFields



    # def missing_sections(self, sections, translatedFields, dfScoringMatrix):

    #     missingFields = {}
    #     for i in range(len(sections)):     
    #         sectionFields = list(dict.fromkeys((dfScoringMatrix.loc[(dfScoringMatrix["Required"]== 1) & (dfScoringMatrix["Section"]==sections[i])].index.values).tolist()))
    #         translatedFields[sections[i]]= {'score':0}

    #         missingFields[sections[i]]=sectionFields

    #     return missingFields




    # def last_item(self, prefix, item, translatedFields, fieldMapping):
    #     """Returns the final value in the json input that does not contain any nested field
        
    #     Arguments:
    #         - prefix: <string> 
    #         - item: <string> 
    #         - allFields: <dictionary> 

    #     """

    #     results = {}
    #     nullCards = ['*','.','?']


    #     translatedKey = self.get_field_name(fieldMapping, prefix)

    #     if((item in nullCards) or (item is None) or (item is False)):
    #         results[translatedKey]= 'Missing'
    #     else:
    #         results[translatedKey]= item

    #     translatedFields[str(prefix)]= str(item)

    #     return results




    def get_field_name(self, fieldMapping, key):

        keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   
        keyDF = fieldMapping[keyNoIndex]

        return keyDF


    def get_field_section(self, fieldMapping, dfScoringMatrix, key):
        section = dfScoringMatrix.loc[[key],['Section']].values[0][0]
        return section

    def get_field_exception(self, fieldMapping, dfScoringMatrix, key):
        exception = dfScoringMatrix.loc[[key],['Exception']].values[0][0]
        return exception




    def exception_APPMETHOD(self, field, section, exception_SEEDEXC):
        """Returns a boolean to indicate if the exception is applicable
        
        Arguments:
            - key: <string> 
            - value: <string> 
            - allFields: <dictionary> 

        Returns:
            - <boolean>
        """

        print("entra a APPMETHOD ", field)




    def exception_SEEDEXC(self, field, section, exception_SEEDEXC):
        print("entra a SEDEXC ", field)







#        print("mmmh" , allFields)

#        fieldtrials.treatments[8].applications[0].products[1].equipment.placement

        # pathSE = ".".join(key.split(".", 2)[:2])
        # pathSE = pathSE + ".standardEvaluationId"

        # SE = (allFields[pathSE]).strip()[0:1]

        # if(SE != value):
        #     if((SE == "P") or(SE == "H")):
        #         return True
        #     else:
        #         return False
        # else:
        #     return False





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
            dfFiltered = df.loc[(df["Trial"] == trialType) & (df["Indication"] == indication)]

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





        # if(len(indexes)==0):
        #     return None

        # if(case == 'subIndex'):
        #     if(len(indexes)>1):
        #         return indexes[1]
        #     else:
        #         return None
        # elif(case == 'mainIndex'):
        #     return indexes[0]
        # else:
        #     if(len(indexes)>2):
        #         return indexes[2]
        #     else:
        #         return None




