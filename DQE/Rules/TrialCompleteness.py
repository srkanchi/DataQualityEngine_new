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
#        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#            print(dfScoringMatrix)

        fieldMapping = self.read_file_mappings(attributeMapping)    # attribute mapping file

        allFields = {}
        resultsFinal = {}

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

        self.find_exceptions(resultsFiltered, dfScoringMatrix)
        self.calculate_scores(resultsFiltered, dfScoringMatrix, allFields, tptIdKey)

        return {
                self.name: {"input": allFields, "translatedInput": resultsFiltered, "version": version
             }
        }




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
        section = dfScoringMatrix.loc[[translatedKey],['Section']].values[0][0]
        required = dfScoringMatrix.loc[[translatedKey],['Required']].values[0][0]


        allFields[prefix]=item

        if(required == 0):
            item= 'Not required'

        elif((item in nullCards) or (item is None) or (item is False)):
            item= 'Missing'


        subIndex = self.get_index(prefix, "subIndex")
        mainIndex = self.get_index(prefix, "mainIndex")

        if subIndex is None:
            resultsRaw[section][mainIndex][0][translatedKey]= str(item) 
        else:
            resultsRaw[section][mainIndex][subIndex][translatedKey]= str(item) 





    def find_exceptions(self, resultsFiltered, dfScoringMatrix):
        """Verifies whether there are exceptions that shoulc be considered
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 

        """



        fieldExceptions = dfScoringMatrix[~dfScoringMatrix['Exception'].isnull()]

        for index, row in fieldExceptions.iterrows():
            if row['Exception'] == "APPMETHOD":
                self.exception_APPMETHOD(index, row['Section'], resultsFiltered, dfScoringMatrix)
            if row['Exception'] == "SEEDEXC":
                self.exception_SEEDEXC(index, row['Section'], resultsFiltered, dfScoringMatrix)



    def exception_APPMETHOD(self, field, section, resultsFiltered, dfScoringMatrix):
        """The soil texture is required only for certain application methods
        
        Arguments:
             - field: <string> 
             - section: <string> 

             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 

        """


        appMethod =['Bed soil incorporation', 'Cover soil incorporation','Drench Incorporated',
                        'Drench', 'Drip', 'Dusting and incorporation', 'Incorporation',
                        'In-Furrow (liquid injection)', 'In-Furrow (on fertiliser)',
                        'Irrigation - Drench', 'Irrigation - Drip', 'Apply over seed (e.g. spreading in furrow)',
                        'Apply under seed (e.g. spreading in furrow)','Seed Treatment, dry',
                        'Seed Treatment, general','Seed Treatment, liquid','Sowing - Planting',
                        'Spreading and incorporation']



        if (section in resultsFiltered) & ("applications" in resultsFiltered):

            if (field in resultsFiltered[section][0]) & (len(resultsFiltered["applications"])>1):

                methodUsed = [a_dict['Application Method'] for a_dict in resultsFiltered["applications"]]

                rightApp = False
                for i in range(len(methodUsed)):     
                    if methodUsed[i] in appMethod:
                        rightApp = True
                        break
                if rightApp == False:
                    resultsFiltered[section][0][field] = 'Not required'
                    dfScoringMatrix.at[field,'Required'] = 0



    def exception_SEEDEXC(self, field, section, resultsFiltered, dfScoringMatrix):
        """Only one: Seed count/seed count unit or seed plant rate/seed plant rate unit is required. Not both 
        
        Arguments:
             - field: <string> 
             - section: <string> 
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 

        """
        #If seed count is present, then seed rate is not needed and viceversa
        
        if section in resultsFiltered:

            if resultsFiltered[section][0][field] != 'Missing':
                resultsFiltered[section][0]['Seed Plant Count']= 'Not required'
                resultsFiltered[section][0]['Seed Plant Count Unit']= 'Not required'
                dfScoringMatrix.at['Seed Plant Count', 'Required'] = 0
                dfScoringMatrix.at['Seed Plant Count Unit', 'Required'] = 0                    
            else:                    
                if resultsFiltered[section][0]['Seed Plant Count'] != 'Missing':
                    resultsFiltered[section][0][field]= 'Not required'
                    resultsFiltered[section][0]['Seed/Plant Rate Unit']= 'Not required'
                    dfScoringMatrix.at[field, 'Required'] = 0
                    dfScoringMatrix.at['Seed/Plant Rate Unit', 'Required'] = 0                    
                elif resultsFiltered[section][0]['Seed/Plant Rate Unit'] != 'Missing':
                    resultsFiltered[section][0]['Seed Plant Count']= 'Not required'
                    resultsFiltered[section][0]['Seed Plant Count Unit']= 'Not required'
                    dfScoringMatrix.at['Seed Plant Count', 'Required'] = 0
                    dfScoringMatrix.at['Seed Plant Count Unit', 'Required'] = 0                    
                elif resultsFiltered[section][0]['Seed Plant Count Unit']!= 'Missing':
                    resultsFiltered[section][0][field]= 'Not required'
                    resultsFiltered[section][0]['Seed/Plant Rate Unit']= 'Not required'
                    dfScoringMatrix.at[field, 'Required'] = 0
                    dfScoringMatrix.at['Seed/Plant Rate Unit', 'Required'] = 0                    
                else:
                    dfScoringMatrix.at[field, 'Required'] = 0
                    dfScoringMatrix.at['Seed/Plant Rate Unit', 'Required'] = 0                    
                    dfScoringMatrix.at['Seed Plant Count', 'Required'] = 1
                    dfScoringMatrix.at['Seed Plant Count Unit', 'Required'] = 1                    




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




    def calculate_scores(self, resultsFiltered, dfScoringMatrix, allFields, tptIdKey):
        """Calculates the final scores taking into account Missing and Not required fields
        
        Arguments:
             - resultsFiltered: <dictionary> 
             - dfScoringMatrix: <dictionary> 
             - allFields: <dictionary> 
             - tptIdKey: <string> 
        """


        sections=list(dict.fromkeys((dfScoringMatrix.loc[dfScoringMatrix["Required"]== 1]['Section'].values).tolist()))


        for key, value in resultsFiltered.items():

            totalFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key) & (dfScoringMatrix["Required"]==1)].index.values.tolist()
            sectionFields = dfScoringMatrix[(dfScoringMatrix["Section"]==key)].index.values.tolist()

            sections.remove(key)
            indexItem =1


            for i in range(len(value)):     

                addFields = list(set(sectionFields) - set(value[i]))

                for j in range(len(addFields)):     
                    if addFields[j] in totalFields:
                        value[i].update({addFields[j]:'Missing'})
                    else:                
                        value[i].update({addFields[j]:'Not required'})


                presentFields = [kk for (kk, vv) in value[i].items() if ((vv != 'Missing') & (vv != 'Not required')) ]

                value[i].update({'score':(len(list(set(totalFields).intersection(presentFields)))/len(totalFields))})
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
             if row['Required'] == 0:
                 missingFields.update({index:'Not required'})
             else:
                 missingFields.update({index:'Missing'})

        missingFields.update({'score':'0'})
        missingFields.update({'trial number':tptIdKey})
        missingFields.update({section + ' number':1})
        
        return missingFields



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
        keyDF = fieldMapping[keyNoIndex]

        return keyDF


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

