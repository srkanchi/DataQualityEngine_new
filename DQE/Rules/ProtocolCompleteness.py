from DQE.Rules.RulesTemplate import RuleTemplate

import pandas as pd
import pprint

import os
import sys
import ast
import re


class ProtocolCompleteness(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(ProtocolCompleteness, self).__init__(rule_name='ProtocolCompleteness', rule_category='data_quality')
    
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

        oTD = TD.create_from_json(data["protocols"][0])

        if (oTD.getTrialType() in ['D','R','A']) and (oTD.getIndication() in ['F','H','I','S','G']):

            general = oTD.getGeneral(attributeMapping, weights)
            finalSummary.update({"General":general})

            treatments = oTD.getTreatments(attributeMapping, weights)


            if len(treatments)>0:
                lstProducts = treatments['Products']
                lstEquipment = treatments['Equipment']

                finalSummary.update({"Treatments":lstProducts})
                finalSummary.update({"Applications":lstEquipment})


            assessments = oTD.getAssessments(attributeMapping, weights)
            finalSummary.update({"Assessments":assessments})


            responsibles = oTD.getResponsibles(attributeMapping, weights)
            finalSummary.update({"Responsibles":responsibles})


        return {
                self.name: {"input": data["protocols"][0], "translatedInput": finalSummary, "version": version
#                self.name: {"input": None, "translatedInput": finalSummary, "version": version
                }
        }




class TD:
    nullChars = ['*','.','?']
    cropUseGroup = ""

    def __init__(self, tptIdKey, keywords, guidelines, dataDeadline, plannedAssessments, treatments, 
        plannedNumberOfApplications, controlField, plotDescription, plotDescriptionBasis, gepCertification,
        plannedNumberOfAssessments, plotArea, plotAreaUnit, siteType, numberOfReplicates, protocolEditionNumber, 
        targets, fieldResponsibles, trialResponsibles, settings, experimentalSeason, crops, projectNumbers, location):

        self.tptIdKey = tptIdKey

        self.keywords = keywords
        self.guidelines =  guidelines
        self.dataDeadline = dataDeadline 
        self.plannedAssessments = plannedAssessments 
        self.treatments = treatments
        self.plannedNumberOfApplications = plannedNumberOfApplications 
        self.controlField = controlField
        self.plotDescription = plotDescription
        self.plotDescriptionBasis = plotDescriptionBasis 
        self.gepCertification = gepCertification
        self.plotArea = plotArea
        self.plotAreaUnit = plotAreaUnit
        self.siteType = siteType
        self.numberOfReplicates = numberOfReplicates
        self.protocolEditionNumber = protocolEditionNumber 
        self.targets = targets
        self.fieldResponsibles = fieldResponsibles
        self.trialResponsibles = trialResponsibles
        self.settings = settings
        self.experimentalSeason = experimentalSeason 
        self.plannedNumberOfAssessments = plannedNumberOfAssessments
        self.crops = crops

        self.cropsGroup = crops


        self.projectNumbers = projectNumbers
        self.location = location



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
    def guidelines(self):
        return self.__guidelines
    @guidelines.setter
    def guidelines(self, guidelines):
        if((guidelines is not None) and (len(guidelines)>0)):
            self.__guidelines = self.listToString(guidelines)
        else:
            self.__guidelines = "Missing"


    @property
    def dataDeadline(self):
        return self.__dataDeadline
    @dataDeadline.setter
    def dataDeadline(self, dataDeadline):
        if((dataDeadline is not None) and (dataDeadline not in self.nullChars)):
            self.__dataDeadline = dataDeadline
        else:
            self.__dataDeadline = "Missing"



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
    def controlField(self):
        return self.__controlField
    @controlField.setter
    def controlField(self, controlField):
        if((controlField is not None) and (controlField not in self.nullChars) and (controlField is not False)):
            self.__controlField = controlField
        else:
            self.__controlField = "Missing"


    @property
    def plotDescription(self):
        return self.__plotDescription
    @plotDescription.setter
    def plotDescription(self, plotDescription):
        if(plotDescription is not None):
            self.__plotDescription = str(plotDescription)
        else:
            self.__plotDescription = "Missing"

    @property
    def plotDescriptionBasis(self):
        return self.__plotDescriptionBasis
    @plotDescriptionBasis.setter
    def plotDescriptionBasis(self, plotDescriptionBasis):
        if((plotDescriptionBasis is not None) and (plotDescriptionBasis not in self.nullChars) and (plotDescriptionBasis is not False)):
            self.__plotDescriptionBasis = plotDescriptionBasis
        else:
            self.__plotDescriptionBasis = "Missing"


    @property
    def gepCertification(self):
        return self.__gepCertification
    @gepCertification.setter
    def gepCertification(self, gepCertification):
        if((gepCertification is not None) and (gepCertification not in self.nullChars) and (gepCertification is not False)):
            self.__gepCertification = gepCertification
        else:
            self.__gepCertification = "Missing"

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
    def siteType(self):
        return self.__siteType
    @siteType.setter
    def siteType(self, siteType):
        if((siteType is not None) and (siteType not in self.nullChars) and (siteType is not False)):
            self.__siteType = siteType
        else:
            self.__siteType = "Missing"


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
    def protocolEditionNumber(self):
        return self.protocolEditionNumber
    @protocolEditionNumber.setter
    def protocolEditionNumber(self, protocolEditionNumber):
        if(protocolEditionNumber is not None):
            self.__protocolEditionNumber = str(protocolEditionNumber)
        else:
            self.__protocolEditionNumber = "Missing"


    @property
    def experimentalSeason(self):
        return self.experimentalSeason
    @experimentalSeason.setter
    def experimentalSeason(self, experimentalSeason):
        if((experimentalSeason is not None) and (experimentalSeason not in self.nullChars)):
            self.__experimentalSeason = experimentalSeason
        else:
            self.__experimentalSeason = "Missing"


    @property
    def targets(self):
        return self.__targets
    @targets.setter
    def targets(self, targets):
        if((targets is not None) and (len(targets)>0)):
#            self.__targets = self.listToString(targets)
            self.__targets = self.listToString(self.getNestedValue(targets, 'targetName'))
        else:
            self.__targets = "Missing"


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


    @property
    def plannedNumberOfAssessments(self):
        return self.__plannedNumberOfAssessments
    @plannedNumberOfAssessments.setter
    def plannedNumberOfAssessments(self, plannedNumberOfAssessments):
        if(plannedNumberOfAssessments is not None):
            self.__plannedNumberOfAssessments = str(plannedNumberOfAssessments)
        else:
            self.__plannedNumberOfAssessments = "Missing"

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
    def location(self):
        return self.__location
    @location.setter
    def location(self, location):
        if((location is not None) and (len(location)>0)):
#            self.__targets = self.listToString(targets)
            self.__location = self.listToString(self.getNestedValue(location, 'country'))
        else:
            self.__location = "Missing"



    @property
    def crops(self):
        return self.__crops
    @crops.setter
    def crops(self, crops):
        if((crops is not None) and (len(crops)>0)):
#            self.__targets = self.listToString(targets)
            self.__crops = self.listToString(self.getNestedValue(crops, 'cropName'))
        else:
            self.__crops = "Missing"



    @staticmethod
    def create_from_json(data):
        return TD(**data)

    def getIndication(self):
        return self.tptIdKey.strip()[0:1]

    def getTrialType(self):
        return self.tptIdKey.strip()[1:2]

    def getRegion(self):
        EMEACountries = ['AUT', 'BEL', 'BGR', 'CZE', 'DEU', 'DNK', 'DZA', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GRC', 'HRV', 'HUN', 'ITA', 'IRL', 'LTU', 'LVA', 'NOR', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'SWE', 'ALB', 'DZA', 'BLR', 'CYP', 'JOR', 'KAZ', 'MAR', 'RUS', 'CHE', 'TUN', 'TUR', 'SRB', 'EUR', 'DVG', 'DRM']        
        protCountry = self.tptIdKey.strip()[4:7]

        if protCountry in EMEACountries and (self.getTrialType() == 'D' or self.getTrialType() == 'R'): 
            return "EMEA"
        else:
            return "GLOBAL"


    def getCropUseGroup(self):
        if((self.cropsGroup is None) or (len(self.cropsGroup)<1)):
            return None
        else:
            return self.listToString(self.getNestedValue(self.cropsGroup, 'useGroupCode'))




    def formatAssessments(self):
        results = []
        for element in self.plannedAssessments:
            listItem = {}
            for key, value in element.items():
                if (isinstance(value, dict)):

                    value = list(value.values())[0]  # The assessments have always a single crop/target
 
                if((value is None) or (value in self.nullChars) or (value is False)):
                    value = "Missing"

                listItem.update({key:value})
            results.append(listItem)
        return results


    def getAssessments(self, attributeMapping, weights):

        results = []
        orderedAssessments = self.formatAssessments()

        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)

        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'assessment') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())
                                & (dfWeights["Required"] >0 )]


#        requiredFields = dfWeightsFiltered.index.values.tolist()
        ruleExceptions = dfWeightsFiltered[~dfWeightsFiltered['Exception'].isnull()]['Exception'].values.tolist()


        for element in orderedAssessments:
            missing = 0
            listItem = {}

            requiredFields = dfWeightsFiltered.index.values.tolist()
            self.checkExceptionsAssessments(ruleExceptions, requiredFields, element)

            for key, value in element.items():
                mapName= mappings[key]

                if(value == "Missing"):
                    if(mapName not in requiredFields):
                        listItem.update({mapName:"Not required"})
                    else:
                        listItem.update({mapName:value})
                        missing = missing +1
                else:
                    listItem.update({mapName:value})

            listItem.update({
               'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
            })

            results.append(listItem)

        return self.removeDuplicatesDict(results)



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
                if(value == "Missing"):                    
                    if(mapName not in requiredFields):
                        results.update({mapName:"Not required"})
                    else:
                        missing = missing + 1
                        results.update({mapName:value})
                else:
                    results.update({mapName:value})

        results.update({
            'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
        })

        return results


    def getTreatments(self, attributeMapping, weights):

        lstResultProducts = []
        lstResultEquipment = []

        lstTreatments = self.formatTreatments() 

        if len(lstTreatments)>0:
            lstProducts = lstTreatments['Products']
            lstEquipment = lstTreatments['Equipment']

            lstResultProducts = self.getScoreProducts(attributeMapping, weights, lstProducts)
            lstResultEquipment = self.getScoreEquipment(attributeMapping, weights, lstEquipment)
            lstResultEquipment = self.removeDuplicatesDict(lstResultEquipment)

        return {'Products':lstResultProducts, "Equipment":lstResultEquipment}


    def getScoreProducts(self, attributeMapping, weights, lstProducts):

        results = []
        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)

        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'treatment') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())
                                & (dfWeights["Required"] >0 )]

#        requiredFields = dfWeightsFiltered.index.values.tolist()
        ruleExceptions = dfWeightsFiltered[~dfWeightsFiltered['Exception'].isnull()]['Exception'].values.tolist()


        for element in lstProducts:
            for item in element:
                missing = 0
                listItem = {}

                requiredFields = dfWeightsFiltered.index.values.tolist()
                self.checkExceptionsTreatments(ruleExceptions, requiredFields, item)

                for key, value in item.items():
                    mapName= mappings[key]

                    if((value is None) or (value in self.nullChars) or (value is False) or (value == "Missing")):
                        if(mapName not in requiredFields):
                            listItem.update({mapName:"Not required"})
                        else:
                            listItem.update({mapName:"Missing"})
                            missing = missing +1
                    else:
                        listItem.update({mapName:value})

                if(self.getRegion=="EMEA"):
                    listItem.update({
                    'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
                    })
                else:
                    listItem.update({'score':"NA"})


                results.append(listItem)

        return results



    def getScoreEquipment(self, attributeMapping, weights, lstEquipment):

        results = []
        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)

        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'application') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())
                                & (dfWeights["Required"] >0 )]

#        requiredFields = dfWeightsFiltered.index.values.tolist()
        ruleExceptions = dfWeightsFiltered[~dfWeightsFiltered['Exception'].isnull()]['Exception'].values.tolist()


        for element in lstEquipment:
            for item in element:
                missing = 0
                listItem = {}

                requiredFields = dfWeightsFiltered.index.values.tolist()
                self.checkExceptionsTreatments(ruleExceptions, requiredFields, item)

                for key, value in item.items():
                    mapName= mappings[key]

                    if((value is None) or (value in self.nullChars) or (value is False) or (value == "Missing")):
                        if(mapName not in requiredFields):
                            listItem.update({mapName:"Not required"})
                        else:
                            listItem.update({mapName:"Missing"})
                            missing = missing +1
                    else:
                        listItem.update({mapName:value})

                listItem.update({
                'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
                })

                results.append(listItem)

        return results



    # def getTreatments(self, attributeMapping, weights):

    #     results = []

    #     dfWeights = self.readWeights(weights)
    #     mappings = self.getFileToDict(attributeMapping)

    #     dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'treatment') 
    #                             & (dfWeights["Region"] == self.getRegion())
    #                             & (dfWeights["Indication"] == self.getIndication())
    #                             & (dfWeights["Trial"] == self.getTrialType())]

    #     requiredFields = dfWeightsFiltered[dfWeightsFiltered["Required"] >0].index.values.tolist()
    #     ruleExceptions = dfWeightsFiltered[~dfWeightsFiltered['Exception'].isnull()]['Exception'].values.tolist()

    #     notRequiredFields = dfWeightsFiltered[dfWeightsFiltered["Required"] ==0].index.values.tolist()

    #     treatments = self.formatTreatments() 


    #     for element in treatments:

    #         self.checkExceptionsTreatments(ruleExceptions, requiredFields, element)


    #         for item in element:
    #             listItem = {}
    #             itemKeys = []
    #             missing = 0
    #             for key, value in item.items():
    #                 mapName= mappings[key]

    #                 if((value is None) or (value in self.nullChars) or (value is False) or (value == "Missing")):
    #                     if(mapName not in requiredFields):                            
    #                         listItem.update({mapName:"Not required"})
    #                     else:
    #                         listItem.update({mapName:"Missing"})
    #                         missing = missing +1
    #                 else:
    #                     itemKeys.append(mapName)
    #                     listItem.update({mapName:value})

    #             missingRequired = list(set(requiredFields) - set(itemKeys))
    #             missingNotRequired = list(set(notRequiredFields) - set(itemKeys))
    #             self.addFields(listItem, missingRequired, "Missing")
    #             self.addFields(listItem, missingNotRequired, "Not required")

                
    #             listItem.update({
    #             'score':str(((len(requiredFields) - len(missingRequired))/len(requiredFields))*100),
    #             })


    #             results.append(listItem)

    #     return results


    def addFields(self, listItem, otherFields, type):
        if len(otherFields)>0:
            for element in otherFields:
                listItem.update({element:type})


    def formatTreatments(self):
        """
        Treatmets have two nested structures: applications and entries, and a single attribute: treatmentKey. 
        Each one is parsed separately
        """

        lstResults = []
        lstProducts = []
        lstEquipment = []

        resultsProducts = []
        resultsEquipment = []

        for element in self.treatments:
            trtKey = element['treatmentKey']
            applications = element['applications']
            entries = element['entries']
            appCodesEntries = []

            if len(entries)<1:
                entries = self.emptyEntries()
            else:
                for i in range(len(entries)):
                    appCodesEntries.append(entries[i].pop("applicationCodes"))     

            lstResults= self.formatApplications(applications, trtKey, self.removeDuplicatesDict(entries))

            if len(lstResults) >0 :
                lstProducts = lstResults['Products']
                lstEquipment = lstResults['Equipment']
                
                lstProducts = self.removeDuplicatesDict(lstProducts)


                if len(lstProducts) == len(appCodesEntries):
                    index =0
                    for item in lstProducts: 
                        item.update({"treatmentKey":trtKey})
                        item.update({"applicationCodes":appCodesEntries[index]})
                        index = index + 1
                else:
                    for item in lstProducts: 
                        item.update({"treatmentKey":trtKey})
                        item.update({"applicationCodes":appCodesEntries[0]})



                resultsProducts.append(lstProducts)
                resultsEquipment.append(lstEquipment)

        return {'Products':resultsProducts, 'Equipment':resultsEquipment}


    def formatApplications(self, applications, trtKey, entries):
        """
        Applications have properties and 1 nested list: products, which are parsed separately
        """
        results = {}
        lstResults = []
        strResults = {}

        dictCrops = {}
        lstProducts = []
        lstEquipment = []    
        for element in applications:
#            index = 0
            tmpEquipment = []
            tmpProducts = {}
            for key, value in element.items():
                if (isinstance(value, list)):
                    if key=="products":    # Products entries stored in lstResults
                        lstResults = self.formatProducts(value)  
                        tmpProducts = lstResults['Products']
                        tmpEquipment = lstResults['Equipment']
                    else: # Crops entries 
                        dictCrops.update(self.formatCrops(value))
                else: # Strings entries stores in strResults 
                    strResults.update({key:value})

                if len(entries) > 0: # Here the entries dictionary is added to the applications entries. 
                    results = entries[0]
 
#            index = index + 1

            results.update(strResults) # Strings are added to the results
            tmpEquipment.update(results)
            tmpEquipment.update(dictCrops)

#            tmpEquipment.update({results})

            #     item = self.mergeDictionaries(item, dictCrops)

            # for item in tmpEquipment:
            #     item = self.mergeDictionaries(item, results)
            #     item = self.mergeDictionaries(item, dictCrops)

            lstEquipment.append(tmpEquipment)
            lstProducts.append(tmpProducts)

        # index=0
        # for item in lstProducts:
        #     lstProducts[index] = self.mergeDictionaries(item, results)
        #     lstProducts[index].update({"treatmentKey":trtKey})
        #     index = index +1


        lstEquipment = self.removeDuplicatesDict(lstEquipment)
#        lstEquipment = lstEquipment


        # index=0
        # for item in lstResults: # the results previously processed are merged with the general list of results
        #     lstResults[index] = self.mergeDictionaries(item, results)
        #     lstResults[index].update({"treatmentKey":trtKey})
        #     index = index +1


        return {'Products':lstProducts, 'Equipment':lstEquipment}




    def formatProducts(self, products):

        lstProducts = {}
        lstEquipment = {}

        for element in products:
            results = {}
            for key, value in element.items(): 
                if key == "equipment":
#                    lstEquipment.append(value)
                    lstEquipment = value
                else:
                    if (isinstance(value, list)):
                        if(len(value)>0):
                            results.update({key:self.listToString(value)})
                    elif (isinstance(value, dict)):
                        results = self.mergeDictionaries(results, value)
                    else:
                        results.update({key:value})

#            lstProducts.append(results)
            lstProducts = results

        return {'Products':lstProducts, 'Equipment':lstEquipment} 



    def getResponsibles(self, attributeMapping, weights):

        results = []
        dfWeights = self.readWeights(weights)
        mappings = self.getFileToDict(attributeMapping)

        dfWeightsFiltered = dfWeights[(dfWeights["Section"] == 'responsible') 
                                & (dfWeights["Region"] == self.getRegion())
                                & (dfWeights["Indication"] == self.getIndication())
                                & (dfWeights["Trial"] == self.getTrialType())]

        requiredFields = dfWeightsFiltered.index.values.tolist()

        for element in self.trialResponsibles:
            missing = 0
            listItem = {}

            for key, value in element.items():
                mapName= mappings[key]

                if((value is None) or (value in self.nullChars) or (value is False)):
                    missing = missing +1
                    value = 'Missing'

                listItem.update({mapName:value})

            listItem.update({
               'score':str(((len(requiredFields)-missing)/len(requiredFields))*100),
            })

            results.append(listItem)

        return self.removeDuplicatesDict(results)




    def formatCrops(self, value):
        if value is None or len(value) <1:   
            return {'cropStageCode': None, 'leafWallArea': None, 'leafWallAreaUnit':None}
        else:
            return value[0]


    def mergeDictionaries(self, dict1, dict2):
        results = {**dict1, **dict2}
        return results



    def emptyEntries(self):
        """ To build the dashboard is easier when all the sections in a TD/Protocol have values
        """
        return [{"tankMixCode": None, "coreOtherTreatments": None, "treatmentRole": None, "applicationCodes": None}]



    def emptyResponsibles(self):
        """ To build the dashboard is easier when all the sections in a TD/Protocol have values
        """
        return [{"hasName": False, "internalValue": None, "plannedNumberOfTrials": None,  "siteName": None, "testType": None}]

    def emptyAssessments(self):
        """ To build the dashboard is easier when all the sections in a TD/Protocol have values
        """

        emptyRecord = {       
            "standardEvaluationId": "Missing",
            "partRated": "Missing",
            "ratingType": "Missing",
            "sampleSize": "Missing",
            "sampleSizeUnit": "Missing",
            "target": "Missing",
            "crop": "Missing",
            "plannedUnit": "Missing",
            "numberOfSubSamples": "Missing",
            "ratingClass": "Missing",
            "assessmentCode": "Missing"
          }

        return [emptyRecord]







    def checkExceptionsAssessments(self, ruleExceptions, requiredFields, element):

        if len(ruleExceptions)>0:
            for item in list(set(ruleExceptions)):
                if item == 'PHSES':
                    self.PHSESException(requiredFields, element)
                if item == 'EFFASS':
                    self.EFFASSException(requiredFields, element)





    def checkExceptions(self, ruleExceptions, requiredFields):

        if len(ruleExceptions)>0:
            for item in ruleExceptions:
                if item == 'EPPO':
                    self.EPPOException(requiredFields)
                if item == 'CROP':
                    self.CROPException(requiredFields)
                if item == 'EFFICACY':
                    self.EFFICACYException(requiredFields)
                if item == 'CROPSAFETY':
                    self.CROPSAFETYException(requiredFields)


    def checkExceptionsTreatments(self, ruleExceptions, requiredFields, element):

        if len(ruleExceptions)>0:
            for item in list(set(ruleExceptions)):
                if item == 'CODE':
                    self.CODEException(requiredFields, element)


    def PHSESException(self, requiredFields, element):
        SE = element["standardEvaluationId"]

        if SE is not None:
            if SE[0:1] == "P" or SE[0:1] == "H":
                requiredFields.remove('Part Rated')
                requiredFields.remove('Crop')

                if element["partRated"] == 'Missing':
                    element["partRated"] = 'Not required'

                if self.getIndication() != 'G':
                    requiredFields.remove('Target')
                    if element["target"] == 'Missing':
                        element["target"] = 'Not required'

                if element["crop"] == 'Missing':
                    element["crop"] = 'Not required'



    def EFFASSException(self, requiredFields, element):
        SE = element["standardEvaluationId"]

        if SE is not None:
            if SE[0:1] == "E":
                requiredFields.remove('Target')

                if element["target"] == 'Missing':
                    element["target"] = 'Not required'



    def CODEException(self, requiredFields, element):
        trtCode = element["productName"]
        trtCat = element["category"]

        if len(trtCode)>0 and (trtCode == 'UNKNOWN_PRODUCT' or trtCat =="Specific Variable Group (e.g. Untreated)" or trtCat == 'Dummy, only for planning in TD'):
            requiredFields.remove('Dose')
            requiredFields.remove('Dose Unit')
            requiredFields.remove('Trans. Dose')
            requiredFields.remove('Trans. Dose Unit')

            if element["quantity"] == 'Missing':
                element["quantity"] = 'Not required'
            if element["productDosageUnit"] == 'Missing':
                element["productDosageUnit"] = 'Not required'
            if element["transferDosage"] == 'Missing':
                element["transferDosage"] = 'Not required'
            if element["transferDosageUnit"] == 'Missing':
                element["transferDosageUnit"] = 'Not required'



  


    def SCOREException(self, requiredFields):
        return False

    def EPPOException(self, requiredFields):
        return False


    def CROPException(self, requiredFields):
        cropGrous= ['C1', 'C2', 'C3', 'C5', 'G1', 'G2', 'G3', 'H4']

        if self.getCropUseGroup() not in cropGrous:
            requiredFields.remove('Plot Description')
            requiredFields.remove('Plot Description Basis')
            if self.plotDescription == 'Missing':
                self.plotDescription = 'Not required'
            if self.plotDescriptionBasis == 'Missing':
                self.plotDescriptionBasis = 'Not required'




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
            dfFiltered = df.loc[df["Case"] == "PROT"]

        except pd.errors.EmptyDataError:
            dfFiltered = pd.DataFrame()

        except:
            raise ValueError("Unexpected error:", sys.exc_info()[0])

        return dfFiltered


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

