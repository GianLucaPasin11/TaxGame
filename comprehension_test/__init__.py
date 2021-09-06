from otree.api import *

doc = """
Comprehension test. If the user fails too many times, they exit.
"""


class Constants(BaseConstants):
    name_in_url = 'comprehension_test'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(label='Giovanni ha uno stipendio di 100$. Deve pagare le tasse data un aliquota del 50%. Se Giovanni dichiara 50$, quante tasse pagherà?',
        choices=[
                    [1, '50$'],
                    [2, '25$'],
                    [3, '0$'],
        ],
        widget=widgets.RadioSelect
    )
    quiz2 = models.IntegerField(label='Giulia prende uno stipendio 100$. Deve pagare le tasse data un aliquota del 30%. Se Giovanni volesse decidere di ossere completamente onesta e pagare tutte le tasse, quanto dovrebbe dichiarare del suo stipendio?',
        choices=[
            [1, '100$'],
            [2, '80$'],
            [3, '27$'],
        ],
        widget=widgets.RadioSelect
        )



class MyPage(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1=2, quiz2=1)

        errors = {f: 'Wrong' for f in solutions if values[f] != solutions[f]}
        # if you don't care about failed attempts, just put:
        # return errors
        # otherwise, do this:
        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 5:
                player.failed_too_many = True
            else:
                return errors


class Failed(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.failed_too_many


class Results(Page):
    pass


page_sequence = [MyPage, Failed, Results]