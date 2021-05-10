from DQE.Rules.RulesTemplate import RuleTemplate
import json
from DQE.Utils.Weights import *
import re
import textwrap


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
            print("For this rule to work, it has to have the inputs of `data`, `upper_bound`, and `lower_bound`. Please refer to documentation.")
            return 1
        except ValueError:
            print("value should be numeric.")
            return 1



    def _rule_definition(self, data, inputs, schema=None):
        """
        """
        scores= {}
        index = 0


        for item in data["trialDescriptions"]:
            keywords = data["trialDescriptions"][index]["keywords"]
            tableWeights= self.select_weights(keywords)

            for element in item:
                #If Json Field value is a Nested Json
                if (isinstance(data["trialDescriptions"][index][element], dict)):
                    self.check_dict(data[element], element, scores, tableWeights)
                #If Json Field value is a list
                elif (isinstance(data["trialDescriptions"][index][element], list)):
                    self.check_list(data["trialDescriptions"][index][element], element, scores, tableWeights)
                else:
                    self.assign_score(element, data["trialDescriptions"][index][element], scores, tableWeights)

            index= index + 1


        totalScoreWeights = self.weights_score(scores)
        missingFields = self.missing_fields(scores, tableWeights)
        totalScoreFields = self.total_fields_score(scores, tableWeights)



        return {
            self.name: {"totalScoureFields":totalScoreFields, "missingFields": missingFields, "totalScoreWeights":totalScoreWeights}
        }





    def check_list(self, ele, prefix, scores, tableWeights):

        for i in range(len(ele)):
            if (isinstance(ele[i], list)):
                self.check_list(ele[i], prefix+"["+str(i)+"]", scores, tableWeights)
            elif (isinstance(ele[i], dict)):
                self.check_dict(ele[i], prefix+"["+str(i)+"]", scores, tableWeights)
            else:
                self.assign_score(prefix, ele[i], scores, tableWeights)



    def check_dict(self, jsonObject, prefix, scores, tableWeights):

        for ele in jsonObject:
            if (isinstance(jsonObject[ele], dict)):
                self.check_dict(jsonObject[ele], prefix+"."+ele, scores, tableWeights)

            elif (isinstance(jsonObject[ele], list)):
                self.check_list(jsonObject[ele], prefix+"."+ele,  scores, tableWeights)
            else:
                self.assign_score(prefix+"."+ele, jsonObject[ele], scores, tableWeights)


    def assign_score(self, ele, dataValue, scores, tableWeights):
#        weightScores = "weights_TD_0"
        nullCards = ['*','.','?','NA']
        NumberTypes = (int, float, complex)

        scorePrefix = re.sub(r'\[(?:[\d,]+)\]', '', ele)        

        if((dataValue not in nullCards) & (dataValue is not None)):
            if("fieldResponsibles" in ele):
                print("Responsibles")
            elif(isinstance(dataValue, bool)):
                scores[scorePrefix]= weights[tableWeights][scorePrefix]
            elif (isinstance(dataValue, NumberTypes)):
                scores[scorePrefix]= weights[tableWeights][scorePrefix]
            elif(len(str.strip(dataValue))>1):
                scores[scorePrefix]= weights[tableWeights][scorePrefix]

        



    def weights_score(self, scores):
        totalScore = 0
        for item in scores:
            totalScore = totalScore +  scores[item]

        return totalScore


    def total_fields_score(self, scores, tableWeights):
        totalFields =0
        totalAvailable = 0
        weightScores = weights[tableWeights]

        for item in weightScores:
            if weightScores[item] > 0:
                totalFields= totalFields+1
                if item in scores:
                    totalAvailable= totalAvailable + 1 

        return totalAvailable/totalFields



    def missing_fields(self, scores, tableWeights):
        weightScores = weights[tableWeights]
        missingFields=[]

        for item in weightScores:
            if weightScores[item] > 0:
                if item not in scores:
                    missingFields.append(item) 


        return missingFields


    def select_weights(self, keywords):

        if "CROPSAFETY" in keywords:
            tableWeights= "weights_TD_0_CROPSAFETY"
        else:
            tableWeights= "weights_TD_0"  


        return tableWeights