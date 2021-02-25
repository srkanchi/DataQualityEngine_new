from DQE.Rules.RulesTemplate import RuleTemplate
from durable.lang import *


score= 0
fields = []


class TDCompleteness(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(TDCompleteness, self).__init__(rule_name='TDCompleteness', rule_category='data_quality')
    
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

        singleScores = {
                "tpt_id_key": 0,
                "year": 0,
                "responsible": 4, 
                "part_rated": 5,
                "assessment_type": 4, 
                "sample_size": 3,
                "sample_size_unit": 3, 
                "number_of_subsamples":2 , 
                "assessment_target": 3, 
                "assessment_crop": 3, 
                "assessment_code": 5, 
                "standard_evaluation": 5, 
                "application_method": 5, 
                "Crop": 5, 
                "objectives": 5, 
                "test_type": 3, 
                "project_number": 4, 
                "responsible_site_code":4 , 
                "gep_code_synonym": 4, 
                "guidelines": 5,
                "site_type":5,
                "technical_mager": 5,
                "no_applications": 3, 
                "no_assessments": 3, 
                "location_of_control": 3, 
                "data_deadline": 5,
                "no_replicates": 4, 
                "no_trials": 4, 
                "experimental_season": 4, 
                "no_harvest": 3, 
                "target": 5}


        with ruleset('TD'):
            @when_all((m.key != ''))
            def tpt_id_key(c):
                global score
                score = score + c.m.score
                fields.append(c.m.attribute)
                c.assert_fact({ 'score': score })


        for key in data:
            value = data[key]
            assert_fact('TD',{ 'key': value, 'score': singleScores[key], 'attribute':key})
        pass


        return {
            self.name: {"score":score, "emptyFields":fields}
        }

