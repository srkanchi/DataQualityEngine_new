from DQE.Rules.RulesTemplate import RuleTemplate
import json
from DQE.Utils.Weights import *
import re
#import textwrap
import collections

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
        scoredData = data["trialDescriptions"] 
        missingFields = []
        score = {"score":0, "scoreMissing":0, "fields":-1}

        keywords = data["trialDescriptions"][0]["keywords"]
        weights= self.select_weights(keywords)

        index = 0 
        for element in data["trialDescriptions"]:
            for item in element:
                if (isinstance(data["trialDescriptions"][index][item], list)):
                    self.check_list(data["trialDescriptions"][index][item], item, missingFields, score, weights)
                else:
                    self.score_no_list(element[item], item, missingFields, score, weights)


            index = index + 1       


        allFields = score["fields"] + len(missingFields) 
        totalScore = (score["fields"]/allFields) * 100 
        allWeightedScores = score["scoreMissing"] + score["score"]
        totalWeightedScores = (score["score"] / allWeightedScores) * 100


        return {
            self.name: {"missingFields": missingFields, "score": totalScore, "weightedScore": totalWeightedScores}                        
        }


    def check_list(self, ele, prefix, missingFields, score, weights):
        if (not ele):
            missingFields.append(prefix)
            score["scoreMissing"] = score["scoreMissing"] + self.find_score(prefix, None, weights)
        else:  
            for item in ele:
                if (isinstance(item, dict)):
                    self.score_nested_dict(ele, prefix, missingFields, score, weights)
                    break
                else:
                    self.score_nested_list(ele, prefix, missingFields, score, weights)
                    break




    def score_nested_dict(self, ele, prefix, missingFields, score, weights):
        nullCards = ['*','.','?','NA']
        NumberTypes = (int, float, complex)

        index = 0

        for element in ele:
            for item in element:      
                if(self.find_score(prefix, item, weights) > 0):
                    if((element[item] not in nullCards) & (element[item] is not None) & (element[item] is not False)):
                        score["score"] = score["score"] + self.find_score(prefix, item, weights)
                        score["fields"] = score["fields"] + 1
                    else:
                        missingFields.append(prefix+"["+str(index)+"]."+item)
                        score["scoreMissing"] = score["scoreMissing"] + self.find_score(prefix, item, weights)

            index= index + 1


    def score_nested_list(self, ele, prefix, missingFields, score, weights):
        nullCards = ['*','.','?','NA']
        emptyV= True

        for element in ele:
            if((element not in nullCards) & (element is not None)):
                emptyV = False


        if(emptyV== False):
            score["fields"] = score["fields"] + 1
            score["score"] = score["score"] + self.find_score(prefix, None, weights)
        else:
            missingFields.append(prefix)
            score["scoreMissing"] = score["scoreMissing"] + self.find_score(prefix, None, weights)


    def score_no_list(self, ele, prefix, missingFields, score, weights):
        nullCards = ['*','.','?','NA']

        if((ele not in nullCards) & (ele is not None)):
            if(isinstance(ele, bool)):
                if (ele==True):
                   score["score"] = score["score"] + self.find_score(prefix, None, weights)
                   score["fields"] = score["fields"] + 1 
                else:
                    missingFields.append(prefix)
                    score["scoreMissing"] = score["scoreMissing"] + self.find_score(prefix, None, weights)

            else:
                score["score"] = score["score"] + self.find_score(prefix, None, weights)
                score["fields"] = score["fields"] + 1 
        else:
            score["scoreMissing"] = score["scoreMissing"] + self.find_score(prefix, None, weights)
            missingFields.append(prefix)



    def find_score(self, prefix,item, weightScores):
        if(item is not None):
            scorePrefix= prefix + "." + item
        else:
            scorePrefix= prefix

        score= weights[weightScores][scorePrefix]        

        return score


    def select_weights(self, keywords):
        tableWeights= "weights_TD_0"  
        if len(keywords) == 1:
            if "CROPSAFETY" in keywords:
                tableWeights= "weights_TD_0_CROPSAFETY"

        return tableWeights


