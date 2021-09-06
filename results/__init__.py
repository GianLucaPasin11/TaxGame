from otree.api import *

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'results'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    round_to_pay = models.IntegerField()
    payoff_to_pay = models.CurrencyField()


# FUNCTIONS
def save_pgg_payoff(player: Player):
    participant = player.participant
    player.round_to_pay = participant.round_to_pay
    player.payoff = participant.payoff_to_pay


# PAGES
class TimeOut(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropout


class Excluded(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropout

    @staticmethod
    def vars_for_template(player: Player):
        save_pgg_payoff(player)
        return dict()


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        save_pgg_payoff(player)
        return dict()


page_sequence = [TimeOut, Excluded, Results]
