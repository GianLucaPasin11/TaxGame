from otree.api import *
import random

doc = """
Implementation of risk preference elicitation method from Eckel and Grossman 2002. Sex differences and statistical stereotyping in attitudes toward financial risk. 
Specifically from Dave et al. 2010. Eliciting risk preferences: When is simple better? (see Appendix)
"""


class Constants(BaseConstants):
    name_in_url = 'page_ri_eg'
    players_per_group = None
    num_rounds = 1

    choice_1_high = 28
    choice_2_high = 36
    choice_3_high = 44
    choice_4_high = 52
    choice_5_high = 60
    choice_6_high = 70

    choice_1_low = 28
    choice_2_low = 24
    choice_3_low = 20
    choice_4_low = 16
    choice_5_low = 12
    choice_6_low = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    timeout_MyPage = models.PositiveIntegerField(initial=0)

    Lotteria = models.PositiveIntegerField(
        choices=[
            [0, "Lotteria 1"],
            [1, "Lotteria 2"],
            [2, "Lotteria 3"],
            [3, "Lotteria 4"],
            [4, "Lotteria 5"],
            [5, "Lotteria 6"],
        ]
    )

    lottery_win = models.FloatField(default=0)

    def calc_pay(player):
        player.participant.vars['lottery_choice'] = player.choice

        player.lottery_win = random.randint(0, 1)
        player.participant.vars['lottery_win'] = player.lottery_win

        list_high = [Constants.choice_1_high, Constants.choice_2_high, Constants.choice_3_high, Constants.choice_4_high,
                     Constants.choice_5_high, Constants.choice_6_high, ]

        list_low = [Constants.choice_1_low, Constants.choice_2_low, Constants.choice_3_low, Constants.choice_4_low,
                    Constants.choice_5_low, Constants.choice_6_low, ]

        if player.lottery_win == 1:
            player.payoff = list_high[player.choice]
        else:
            player.payoff = list_low[player.choice]

        player.participant.vars['risk_lottery_payoff'] = player.payoff

class MyPage(Page):
    form_model = 'player'
    form_fields = ['Lotteria']
    timer_text = 'Time left to complete your decisions:'

    # def get_timeout_seconds(player):
    #     return (player.participant.vars['expiry'] - datetime.datetime.utcnow()).total_seconds()

        # def vars_for_template(player):
        #     return {'email': player.session.config['email']}

    def before_next_page(player: Player, timeout_happened):
            player.calc_pay()

            if timeout_happened:
                player.timeout_MyPage = 1


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(player):
        pass


class Results(Page):
    pass


page_sequence = [
    MyPage,
    #ResultsWaitPage,
    Results
]