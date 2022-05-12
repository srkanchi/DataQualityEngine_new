from DQE.Rules.RulesTemplate import RuleTemplate

import pandas as pd
import pprint

import os
import sys
import ast
import re


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
#            cropGroups = inputs['cropGroups']

            attributeMapping = inputs['attributeMapping']

            if weights is None:
                raise ValueError("The weight matrix is empty.")
            if version is None:
                raise ValueError("The version is empty.")
            if attributeMapping is None:
                raise ValueError("The attribute mapping file is empty.")
#            if cropGroups is None:
#                raise ValueError("The crop file is empty.")

            return 0

        except KeyError:
            print("For this rule to work, it has to have the input of `data`. Please refer to documentation.")
            return 1


    def _rule_definition(self, data, inputs, schema=None):
        weights = inputs['weights']
        version = inputs['version']
#        cropGroups = inputs['cropGroups']

        attributeMapping = inputs['attributeMapping']

        if weights is None:
            raise ValueError("The weight matrix is empty.")
        if version is None:
            raise ValueError("The version is empty.")
        if attributeMapping is None:
            raise ValueError("The attribute mapping file is empty.")
#        if cropGroups is None:
#            raise ValueError("The crop file is empty.")


        finalSummary = {}

        oTD = TD.create_from_json(data["trialDescriptions"][0])

        if (oTD.getTrialType() in ['D','R','A']) and (oTD.getIndication() in ['F','H','I','S','G']):

            lstGeneral = []
            general = oTD.getGeneral(attributeMapping, weights)
            lstGeneral.append(general)
            finalSummary.update({"General":lstGeneral})


            responsibles = oTD.getResponsibles(attributeMapping, weights)
            finalSummary.update({"Responsibles":responsibles})


        return {
                self.name: {"input": data["trialDescriptions"][0], "translatedInput": finalSummary, "version": version
                }
        }




class TD:
    nullChars = ['*','.','?']

    def __init__(self, tptIdKey, trialResponsibles, siteType, keywords, experimentalSeason, numberOfReplicates,
        targets, protocolEditionNumber, fieldResponsibles, guidelines, plotArea, plotAreaUnit, 
        plannedNumberOfApplications, dataDeadline, crops, projectNumbers, settings):


        self.tptIdKey = tptIdKey
        self.trialResponsibles = trialResponsibles
        self.siteType = siteType
        self.keywords = keywords
        self.experimentalSeason = experimentalSeason
        self.numberOfReplicates = numberOfReplicates
        self.targets = targets
        self.protocolEditionNumber = protocolEditionNumber
        self.fieldResponsibles = fieldResponsibles
        self.guidelines = guidelines
        self.plotArea = plotArea
        self.plotAreaUnit = plotAreaUnit
        self.plannedNumberOfApplications = plannedNumberOfApplications
        self.dataDeadline = dataDeadline
        self.crops = crops
        self.projectNumbers = projectNumbers
        self.settings = settings


    @property
    def siteType(self):
        return self.__siteType
    @siteType.setter
    def siteType(self, siteType):
        if((siteType is not None) and (siteType not in self.nullChars) and (siteType is not False)):
            self.__siteType = siteType
        else:
            self.__siteType = "Missing"

    @property
    def keywords(self):
        return self.__keywords
    @keywords.setter
    def keywords(self, keywords):
        if((keywords is not None) and (len(keywords) > 0)):
            self.__keywords = self.listToString(keywords)
        else:
            self.__keywords = "Missing"

    @property
    def experimentalSeason(self):
        return self.__experimentalSeason
    @experimentalSeason.setter
    def experimentalSeason(self, experimentalSeason):
        if((experimentalSeason is not None) and (experimentalSeason not in self.nullChars) and (experimentalSeason is not False)):
            self.__experimentalSeason = experimentalSeason
        else:
            self.__experimentalSeason = "Missing"


    @property
    def numberOfReplicates(self):
        return self.__numberOfReplicates
    @numberOfReplicates.setter
    def numberOfReplicates(self, numberOfReplicates):
        if(numberOfReplicates is not None):
            self.__numberOfReplicates = str(numberOfReplicates)
        else:
            self.__numberOfReplicates = "Missing"


    @property
    def targets(self):
        return self.__targets
    @targets.setter
    def targets(self, targets):
        if((targets is not None) and (len(targets)>0)):
#            self.__targets = self.listToString(targets)
            self.__targets = self.listToString(self.getNestedValue(targets, 'name'))
        else:
            self.__targets = "Missing"


    @property
    def protocolEditionNumber(self):
        return self.protocolEditionNumber
    @protocolEditionNumber.setter
    def protocolEditionNumber(self, protocolEditionNumber):
        if(protocolEditionNumber is not None):
            self.__protocolEditionNumber = str(protocolEditionNumber)
        else:
            self.__protocolEditionNumber = "Missing"



    @property
    def guidelines(self):
        return self.__guidelines
    @guidelines.setter
    def guidelines(self, guidelines):
        if((guidelines is not None) and (len(guidelines)>0)):
            self.__guidelines = self.listToString(guidelines)
        else:
            self.__guidelines = "Missing"


    @property
    def plotArea(self):
        return self.plotArea
    @plotArea.setter
    def plotArea(self, plotArea):
        if(plotArea is not None):
            self.__plotArea = str(plotArea)
        else:
            self.__plotArea = "Missing"



    @property
    def plotAreaUnit(self):
        return self.plotAreaUnit
    @plotAreaUnit.setter
    def plotAreaUnit(self, plotAreaUnit):
        if((plotAreaUnit is not None) and (plotAreaUnit not in self.nullChars)):
            self.__plotAreaUnit = plotAreaUnit
        else:
            self.__plotAreaUnit = "Missing"


    @property
    def plannedNumberOfApplications(self):
        return self.__plannedNumberOfApplications
    @plannedNumberOfApplications.setter
    def plannedNumberOfApplications(self, plannedNumberOfApplications):
        if(plannedNumberOfApplications is not None):
            self.__plannedNumberOfApplications = str(plannedNumberOfApplications)
        else:
            self.__plannedNumberOfApplications = "Missing"


    @property
    def dataDeadline(self):
        return self.dataDeadline
    @dataDeadline.setter
    def dataDeadline(self, dataDeadline):
        if((dataDeadline is not None) and (dataDeadline not in self.nullChars)):
            self.__dataDeadline = dataDeadline[0:10]
        else:
            self.__dataDeadline = "Missing"


    @property
    def crops(self):
        return self.__crops
    @crops.setter
    def crops(self, crops):
        if((crops is not None) and (len(crops)>0)):
            self.__crops = self.listToString(self.getNestedValue(crops, 'name'))
#            self.__crops = self.getNestedValue(crops, 'name')
        else:
            self.__crops = "Missing"


    @property
    def projectNumbers(self):
        return self.__projectNumbers
    @projectNumbers.setter
    def projectNumbers(self, projectNumbers):
        if((projectNumbers is not None) and (len(projectNumbers) > 0)):
            self.__projectNumbers = self.listToString(projectNumbers)
        else:
            self.__projectNumbers = "Missing"


    @property
    def settings(self):
        return self.__settings
    @settings.setter
    def settings(self, settings):
        if((settings is not None) and (len(settings)>0)):
            self.__settings = self.listToString(self.getNestedValue(settings, 'conductUnderGLPAndGEP'))
        else:
            self.__settings = "Missing"


    @property
    def fieldResponsibles(self):
        return self.__fieldResponsibles
    @fieldResponsibles.setter
    def fieldResponsibles(self, fieldResponsibles):
        if((fieldResponsibles is not None) and (len(fieldResponsibles)>0)):
            self.__fieldResponsibles = self.getTechnicalManager(fieldResponsibles)
        else:
            self.__fieldResponsibles = "Missing"




    @staticmethod
    def create_from_json(data):
        return TD(**data)

    def getIndication(self):
        return self.tptIdKey.strip()[0:1]

    def getTrialType(self):
        return self.tptIdKey.strip()[1:2]

    def getRegion(self):
#       keyNoIndex = re.sub(r'\[(?:[\d,]+)\]', '', key)   

#        pattern = re.sub(r'^\DR|D\d+EUR.*R$', '', self.tptIdKey)   
        pattern = '^\D(R|D)\w+EUR\w+R$'
        result = re.match(pattern, self.tptIdKey)

        if result:
            return "EMEA"
        else:
            return "GLOBAL"



    def getGeneral(self, attributeMapping, weights):

        results = {}
        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)



        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'general') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())
                                & (dfWeights["Required"] >0 )]


        requiredFields = dfWeightsFiltered.index.values.tolist()
        ruleExceptions = dfWeightsFiltered[~dfWeightsFiltered['Exception'].isnull()]['Exception'].values.tolist()

        self.checkExceptions(ruleExceptions, requiredFields)

        missing = 0
        for property, value in vars(self).items():
            if property.startswith("_"):
                mapName= mappings[property[5:]]    
                if(value is "Missing"):
                    if(mapName not in requiredFields):
                        results.update({mapName:"Not required"})
                    else:
                        missing = missing + 1
                        results.update({mapName:value})
                else:
                    results.update({mapName:str(value)})


        results.update({
 #           'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
            'score':str(round(((len(requiredFields)-missing)/len(requiredFields))*100,2)),

        })

        return results



    def getResponsibles(self, attributeMapping, weights):

        results = []
        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)

        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'responsible') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())]

        requiredFields = dfWeightsFiltered.index.values.tolist()


        if len(self.trialResponsibles) <1:
            self.trialResponsibles= self.emptyResponsibles()



        for element in self.trialResponsibles:
            missing = 0
            listItem = {}

            for key, value in element.items():
                mapName= mappings[key]

                if((value is None) or (value in self.nullChars) or (value is False)):
                    missing = missing +1
                    value = 'Missing'

                listItem.update({mapName:str(value)})

            listItem.update({
#               'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
               'score':str(round(((len(requiredFields)-missing)/len(requiredFields))*100,2)),

            })

            results.append(listItem)

        return self.removeDuplicatesDict(results)







    def checkExceptions(self, ruleExceptions, requiredFields):

        if len(ruleExceptions)>0:
            for element in ruleExceptions:
#                if element == 'EPPO':
#                    self.EPPOException(requiredFields)
                if element == 'EFFICACY':
                    self.EFFICACYException(requiredFields)
                if element == 'CROPSAFETY':
                    self.CROPSAFETYException(requiredFields)


#    def EPPOException(self, requiredFields):
#        EPPOCountries = ['AUT', 'BEL', 'BGR', 'CZE', 'DEU', 'DNK', 'DZA', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GRC', 'HRV', 'HUN', 'ITA', 'IRL', 'LTU', 'LVA', 'NOR', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'SWE']
#        return False



    def EFFICACYException(self, requiredFields):
        if (self.keywords.find('EFFICACY')== -1):
            requiredFields.remove('Target')
            if self.targets == 'Missing':
                self.__targets = "Not required"



    def CROPSAFETYException(self, requiredFields):

        if(((self.keywords == "CROPSAFETY") or (self.keywords == "SELECTIVITY"))):
            requiredFields.remove('Target')
            if self.targets == 'Missing':
                self.__targets = "Not required"

 
    def getTechnicalManager(self, fieldResponsibles):
        result = 'Missing'
        for element in fieldResponsibles:
            if 'Technical Manager' in list(element.values()):
                return "Yes"

        return result


    def readWeights(self, weights):
        """Returns a dataframe that contains the weights used to calculate the scores. 
        The dataframe is filtered to contain only the correspondant indication and trial type   
        """
        try:
            dfWeights = os.path.join(weights)
            df = pd.read_csv(dfWeights, delimiter=",", index_col="Field", converters=None)
#            dfFiltered = df.loc[(df["Status"] == 0) & (df["Trial"] == self.getTrialType())  & (df["Indication"] == self.getIndication()) & (df["Region"] == self.getRegion()) ]
            dfFiltered = df.loc[df["Case"] == "TD 0"]

        except pd.errors.EmptyDataError:
            dfFiltered = pd.DataFrame()

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])

        return dfFiltered



    def emptyResponsibles(self):
        """ To build the dashboard is easier when all the sections in a TD/Protocol have values
        """
        return [{"hasName": False, "internalValue": None, "plannedNumberOfTrials": None,  "siteName": None, "testType": None}]


    def listToString(self, item):
        results = None
        results = ', '.join(item)
        return results


    def numListToString(self, item):
        results = None
        results = ''.join(str(e) for e in item)
        return results


    def getNestedValue(self, jsonVar, label):
        arr = []
        values = self.extract(jsonVar, arr, label)
        noDuplicates = list(set(values))

        return noDuplicates

    def extract(self, obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    self.extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                self.extract(item, arr, key)
        return arr

    def removeDuplicatesDict(self, orderedLista):
        results = [dict(t) for t in {tuple(d.items()) for d in orderedLista}]
        return results


    def getFileToDict(self, path):
        try:
            f = open(path, "r")
            contents = f.read()
            fileDict = ast.literal_eval(contents)

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])
        return fileDict
