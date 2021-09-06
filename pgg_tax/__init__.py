from otree.api import *
from random import shuffle, randint
from itertools import cycle

c = Currency

doc = """
Your app description
"""

# TODO: eclusion and dropout logic to be revised entirely


class Constants(BaseConstants):
    name_in_url = 'pggtax'
    players_per_group = 2  # 4
    num_rounds = 4  # 20

    rounds_with_belief_cond = [1, 3]
    round_treatment_switch = num_rounds // 2

    endowment = cu(100)
    tax_rate = 30
    tax_rate_percent = 0.30
    multipliers = [0.5, 0.5, 2, 2]
    multiplier_switch = {0.5: 2, 2: 0.5}
    info = [False, True]

    belief_cond_fields = [f'cond_emp_{m + 1}' for m in range(3)] + [f'cond_norm_{n + 1}' for n in range(3)]
    belief_cond_maxmin = ['10$?', '15$?', '20$?'] * 2

    timers = dict(decision=60 * 0.2, belief=60 * 2, belief_cond=60 * 4, results=60 * 1)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    has_dropout = models.BooleanField(initial=False)
    multiplier = models.FloatField()
    info = models.BooleanField()
    tot = models.CurrencyField()
    share = models.CurrencyField()


class Player(BasePlayer):
    dropout = models.BooleanField(initial=False)

    income = models.CurrencyField(label='', min=0, max=Constants.endowment)
    tax_paid = models.CurrencyField()

    personalnormative = models.CurrencyField(label='', min=0, max=Constants.endowment)

    empirical1 = models.CurrencyField(label='', min=0, max=Constants.endowment)
    empirical2 = models.CurrencyField(label='', min=0, max=Constants.endowment)
    empirical3 = models.CurrencyField(label='', min=0, max=Constants.endowment)

    normative1 = models.CurrencyField(label='', min=0, max=Constants.endowment)
    normative2 = models.CurrencyField(label='', min=0, max=Constants.endowment)
    normative3 = models.CurrencyField(label='', min=0, max=Constants.endowment)

    condcont1 = models.CurrencyField(label='Dichiara 50$ o di più a testa e crede che lei debba dichiarare 50$ o di più?', min=0, max=Constants.endowment)
    condcont2 = models.CurrencyField(label='Dichiara 50$ o di più a testa e crede che lei debba dichiarare 50$ o di meno?', min=0, max=Constants.endowment)
    condcont3 = models.CurrencyField(label='Dichiara 50$ o di meno a testa e crede che lei debba dichiarare 50$ o di più?', min=0, max=Constants.endowment)
    condcont4 = models.CurrencyField(label='Dichiara 50$ o di meno a testa e crede che lei debba dichiarare 50$ o di meno?', min=0, max=Constants.endowment)

    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(
        label='Giovanni ha uno stipendio di 100$. Deve pagare le tasse data aliquota del 50%. Se Giovanni dichiara 50$, quante tasse pagherà?',
        choices=[
            [1, '50$'],
            [2, '25$'],
            [3, '0$'],
        ],
        widget=widgets.RadioSelect
        )
    quiz2 = models.IntegerField(
        label='Giulia prende uno stipendio 100$. Deve pagare le tasse data aliquota del 30%. Se Giulia volesse pagare tutte le tasse, quanto dovrebbe dichiarare del suo stipendio?',
        choices=[
            [1, '100$'],
            [2, '80$'],
            [3, '27$'],
        ],
        widget=widgets.RadioSelect
        )

    for n, f in enumerate(Constants.belief_cond_fields):
        l = 'How much are you willing to contribute given that your peers contributed' if 'emp' in f else 'How much are you willing to contribute given that your peers think is right to contribute'
        locals()[f] = models.CurrencyField(
            label=l + f' {Constants.belief_cond_maxmin[n]}',
            min=0, max=Constants.endowment
        )
    del n, f, l


# What in your opinion will be the average number reported by other participants of this study?
# FUNCTIONS
def set_participant_vars_default(session: Subsession.session):
    for p in session.get_participants():
        p.excluded, p.dropout, p.pgg_tax_endowment = False, False, 0


def creating_session(subsession: Subsession):
    const = Constants

    multipliers = cycle(const.multipliers)
    info = cycle(const.info)
    if subsession.round_number == 1:
        session = subsession.session
        config = session.config
        set_participant_vars_default(session)

        ps = subsession.get_players()
        shuffle(ps)
        group_matrix = [ps[n:n + const.players_per_group] for n in range(0, len(ps), const.players_per_group)]
        subsession.set_group_matrix(group_matrix)
        groups = subsession.get_groups()

        for g in groups:
            g.multiplier = next(multipliers)
            g.info = config.get('info', next(info))
    else:
        subsession.group_like_round(1)

        groups = subsession.get_groups()
        for g in groups:
            prev_g = g.in_round(1)
            prev_multiplier = prev_g.multiplier
            g.info = prev_g.info
            if subsession.round_number <= const.round_treatment_switch:
                g.multiplier = prev_multiplier
            else:
                g.multiplier = const.multiplier_switch[prev_multiplier]


def set_tax_paid(player: Player):
    player.tax_paid = player.income * Constants.tax_rate_percent


def set_payoffs(group: Group):
    update_group(group)
    if group.has_dropout:
        for p in group.get_players():
            set_participant_payoff(p)
        return

    const = Constants
    ps = group.get_players()
    # Total of taxed paid in the group
    tot = sum(p.tax_paid for p in ps)
    share = tot * group.multiplier / len(ps)
    group.tot = tot
    group.share = share
    for p in ps:
        p.payoff = p.participant.pgg_tax_endowment - p.tax_paid + share


def update_group(group: Group):
    ps = group.get_players()
    for p in ps:
        if p.dropout:
            group.has_dropout = True
            break

    if group.has_dropout:
        for p in ps:
            if not p.dropout:
                p.participant.excluded = True


def set_participant_payoff(player: Player):
    # TODO: update to deal with excluded players caused by dropouts
    participant = player.participant
    round_to_pay = randint(1, player.round_number)
    payoff_to_pay = player.in_round(round_to_pay).payoff
    participant.round_to_pay = round_to_pay
    participant.payoff_to_pay = payoff_to_pay


# PAGES

class TaskPage(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.dropout = True
            player.participant.dropout = True
            player.group.has_dropout = True
        elif player.group.has_dropout:
            player.participant.excluded = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout or participant.excluded:
            return upcoming_apps[-1]


class GroupingPage(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class NextTaskIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.round_treatment_switch + 1


class Instructions(Page):
    pass


class Example(Page):
    pass

class Comprehension(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1=2, quiz2=1)

        errors = {f: 'Wrong' for f in solutions if values[f] != solutions[f]}
        # if you don't care about failed attempts, just put:
        return errors
        # otherwise, do this:
        # if errors:
        #     player.num_failed_attempts += 1
        #     if player.num_failed_attempts >= 5:
        #         player.failed_too_many = True
        #     else:
        #         return errors

class Decision(TaskPage):
    form_model = 'player'
    form_fields = ['income']
    timeout_seconds = Constants.timers['decision']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(high=player.group.multiplier == Constants.multipliers[-1])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        super(Decision, Decision).before_next_page(player, timeout_happened)
        if not timeout_happened:
            set_tax_paid(player)


class PNB(Page):
    form_model = 'player'
    form_fields = ['personalnormative']

class EE(Page):
    form_model = 'player'
    form_fields = ['empirical1', 'empirical2', 'empirical3']

class NE(Page):
    form_model = 'player'
    form_fields = ['normative1', 'normative2', 'normative3']

class CondCont(Page):
    form_model = 'player'
    form_fields = ['condcont1', 'condcont2', 'condcont3', 'condcont4']


# class Beliefs(TaskPage):
#     form_model = 'player'
#     form_fields = ['personalnormative', 'empirical', 'normative']
#     timeout_seconds = Constants.timers['belief']
#
#     # @staticmethod
#     # def vars_for_template(player: Player):
#     #     return dict(high=player.group.multiplier == Constants.multipliers[-1])
#
# class BeliefsCond(TaskPage):
#     form_model = 'player'
#     form_fields = Constants.belief_cond_fields
#     timeout_seconds = Constants.timers['belief_cond']
#
#     @staticmethod
#     def is_displayed(player: Player):
#         return player.round_number in Constants.rounds_with_belief_cond


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        set_payoffs(group)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout or participant.excluded:
            return upcoming_apps[-1]


class Results(TaskPage):
    timeout_seconds = Constants.timers['results']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(high=player.group.multiplier == Constants.multipliers[-1])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        super(Results, Results).before_next_page(player, timeout_happened)
        if player.round_number == Constants.num_rounds:
            set_participant_payoff(player)


page_sequence = [NextTaskIntro,
                 Instructions,
                 Example,
                 Comprehension,
                 PNB,
                 EE,
                 NE,
                 CondCont,
                 Decision,
                 #Beliefs,
                 #BeliefsCond,
                 ResultsWaitPage,
                 Results
                 ]
