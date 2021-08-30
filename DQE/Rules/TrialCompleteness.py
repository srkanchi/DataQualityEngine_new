from DQE.Rules.RulesTemplate import RuleTemplate
#from durable.lang import *
import json
#from DQE.Utils.Weights import *
import re

score= 0
mandatoryFields = []
emptyFields = []
nullCards = ['*','.','?']




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
        NumberTypes = (int, float, complex)
        indication=str(data["name"])[0:1]
        trialType=str(data["name"])[1:2]

        whichScores = "weights_" + trialType + "_" + indication

        #Iterating all the fields of the JSON
        for element in data:

        #If Json Field value is a Nested Json
            if (isinstance(data[element], dict)):
                self.check_dict(data[element], element, whichScores)
            #If Json Field value is a list
            elif (isinstance(data[element], list)):
                self.check_list(data[element], element, whichScores)
                self.calculate_score(element, whichScores)
            #If Json Field value is a string
            elif (isinstance(data[element], NumberTypes)):
#                self.print_field(data[element], element)
                self.calculate_score(element, whichScores)
            elif (isinstance(data[element], str)):
                if((len(str.strip(data[element]))>1 ) & (data[element] not in nullCards)):
#                    self.print_field(data[element], element)
                    self.calculate_score(element, whichScores)
                else:
                    emptyFields.append(element)
            else:
                emptyFields.append(element)


        print ("Empty fields: ")
        print(*emptyFields, sep = "\n") 

        return {
            self.name: {"score":score, "mandatoryFields": mandatoryFields}
        }


        

    def check_list(self, ele, prefix, whichScores):
        NumberTypes = (int, float, complex)

        for i in range(len(ele)):

            if (isinstance(ele[i], list)):
                self.check_list(ele[i], prefix+"["+str(i)+"]", whichScores)
#            elif (isinstance(ele[i], NumberTypes)):
#                self.print_field(ele[i], prefix+"["+str(i)+"]")
            elif (isinstance(ele[i], dict)):
                self.check_dict(ele[i], prefix+"["+str(i)+"]", whichScores)
            elif (isinstance(ele[i], str)):
                if((len(str.strip(ele[i]))>1 ) & (ele[i] not in nullCards)):
#                   self.print_field(ele[i], prefix+"["+str(i)+"]")
                   self.calculate_score(ele[i], whichScores)
                else:
                    emptyFields.append(i)



    def check_dict(self, jsonObject, prefix, whichScores):
        NumberTypes = (int, float, complex)

        for ele in jsonObject:
            if (isinstance(jsonObject[ele], dict)):
                self.check_dict(jsonObject[ele], prefix+"."+ele, whichScores)

            elif (isinstance(jsonObject[ele], list)):
                self.check_list(jsonObject[ele], prefix+"."+ele, whichScores)

            elif (isinstance(jsonObject[ele], str)):
                if((len(str.strip(jsonObject[ele]))>1 ) & (jsonObject[ele] not in nullCards)):
                   self.calculate_score(prefix+"."+ele, whichScores)
                else:
                    emptyPrefix = prefix+"."+ele
                    emptyFields.append(emptyPrefix)

            elif (isinstance(jsonObject[ele], NumberTypes)):
                self.calculate_score(prefix+"."+ele, whichScores)
            else:
                emptyPrefix = prefix+"."+ele
                emptyFields.append(emptyPrefix)



#    def print_field(self, ele, prefix):
#        print (prefix, ":" , ele)

    def calculate_score(self, ele, whichScores):
        global score
        global weights

        scorePrefix = re.sub(r'\[(?:[\d,]+)\]', '', ele)

        score = score + weights[whichScores][scorePrefix]
        if ele not in mandatoryFields:
            mandatoryFields.append(ele)
#            print ("Field {0} and score: " , ele, weights[whichScores][scorePrefix])
#            print ("new score: ", score)
#            print ("campos: ", mandatoryFields)



