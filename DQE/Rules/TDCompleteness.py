from DQE.Rules.RulesTemplate import RuleTemplate
from durable.lang import *

class TDCompleteness(RuleTemplate):
    """
    class description here
    """

    def __init__(self):
        super(TDCompleteness, self).__init__(rule_name='TDCompleteness', rule_category='data_quality')
    
    def _rule_input_check(self, **kwargs):
        """
        """
        try:
            data = kwargs['data']
            return 0
        except KeyError:
            print("For this rule to work, it has to have the inputs of `data`, `upper_bound`, and `lower_bound`. Please refer to documentation.")
            return 1
        except ValueError:
            print("value should be numeric.")
            return 1

    def _rule_definition(self, **kwargs):
        """
        """
        data = kwargs.get('data')

        rtn = []

        with ruleset('animal'):
            # will be triggered by 'Kermit eats flies'
            @when_all((m.predicate == 'eats') & (m.object == 'flies'))
            def frog(c):
                c.assert_fact({ 'subject': c.m.subject, 'predicate': 'is', 'object': 'frog' })

            @when_all((m.predicate == 'eats') & (m.object == 'worms'))
            def bird(c):
                c.assert_fact({ 'subject': c.m.subject, 'predicate': 'is', 'object': 'bird' })

            # will be chained after asserting 'Kermit is frog'
            @when_all((m.predicate == 'is') & (m.object == 'frog'))
            def green(c):
                c.assert_fact({ 'subject': c.m.subject, 'predicate': 'is', 'object': 'green' })

            @when_all((m.predicate == 'is') & (m.object == 'bird'))
            def black(c):
                c.assert_fact({ 'subject': c.m.subject, 'predicate': 'is', 'object': 'black' })

            @when_all(+m.subject)
            def output(c):
                rtn.append('Fact: {0} {1} {2}'.format(c.m.subject, c.m.predicate, c.m.object))

        assert_fact('animal', { 'subject': 'Kermit', 'predicate': 'eats', 'object': 'flies' })

        return {
            self.name: rtn
        }

