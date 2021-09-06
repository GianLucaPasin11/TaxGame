from otree.api import *

c = Currency

doc = """
Real effort task, based on moving sliders, as in:
Gill, David, and Victoria Prowse. 2012.
"A Structural Analysis of Disappointment Aversion in a Real Effort Competition."
American Economic Review, 102 (1): 469-503.
DOI: 10.1257/aer.102.1.469
"""


class Constants(BaseConstants):
    name_in_url = 'sliders_task'
    players_per_group = None
    num_rounds = 1

    # Set task parameters
    sliders_task_pms = dict(
        time_in_seconds=60 * 2,
        num=48, ncols=3,
        max=100, min=0,
        target=50,
        default='min',          # Sliders default value when the task begin
        num_centered=0,
        bonus_per_slider=10,
        bonus=cu(0)
    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    num_centered = models.IntegerField()
    excluded = models.BooleanField(initial=False)


# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        session = subsession.session
        config = session.config
        const = Constants
        sliders_task_pms = const.sliders_task_pms.copy()
        if 'ret_slider_num' in config:
            sliders_task_pms.update(
                num=config['ret_slider_num'],
                ncols=config['ret_slider_ncols'],
                bonus_per_slider=config['bonus_per_slider']
            )
        session.sliders_task_pms = sliders_task_pms


def set_excluded_player(player: Player, num_centered: int):
    if num_centered < player.session.sliders_task_pms['num']:
        player.excluded = True
        player.participant.excluded = True


def set_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def set_sliders_task(player: Player, const: Constants):
    # Import module needed
    from random import randint, choice

    # Copy task parameters from Constants (which therefore will remain unchanged)
    session = player.session
    task = session.sliders_task_pms.copy()

    # Set random value for left margin of sliders in each row
    offsets = [randint(0, 10) for _ in range(task['num'] // task['ncols'])]

    # Set default values of sliders: either to "min" or to random values
    if task['default'] == 'min':
        m = task['min']
        curr_values = [m for _ in range(task['num'])]
    else:
        input_range = list(range(task['min'], task['max']))
        input_range.remove(task['target'])
        curr_values = [choice(input_range) for _ in range(task['num'])]

    # Set list of rows containing the sliders: each row contains 3 sliders and the left margin for that row
    sliders = list(zip(set_chunks(curr_values, task['ncols']), offsets))

    # Flag task as set
    task_set = True

    # Update dictionary containing task parameters
    task.update(offsets=offsets, curr_values=curr_values, sliders=sliders)

    return task_set, task


# PAGES
class PreRet(Page):
    pass


class SliderTask(Page):
    timeout_seconds = Constants.sliders_task_pms['time_in_seconds']
    timer_text = 'Remaining time: '

    @staticmethod
    def vars_for_template(player: Player):
        pvars = player.participant.vars
        # If no task exists yet, set a new task
        if not pvars.get('sliders_task_set'):
            pvars['sliders_task_set'], pvars['sliders_task'] = set_sliders_task(player, Constants)

        # Returns the dictionary containing the task parameters as variables for the template
        return pvars['sliders_task']

    @staticmethod
    def live_method(player: Player, data):
        sliders_task_pms = player.session.sliders_task_pms
        participant = player.participant

        # Get task parameters
        task = participant.vars['sliders_task']

        # Get updated number of centered sliders
        num_centered = len([v for v in data if v == task['target']])

        # Update task parameters based on: current values of the sliders, number of centered sliders, bonus accumulated
        task.update(
            sliders=list(zip(set_chunks(data, task['ncols']), task['offsets'])),
            num_centered=num_centered,
            bonus=num_centered * task['bonus_per_slider'],
            finished=num_centered == sliders_task_pms['num']
        )

        # Send updated task's parameters to the webpage
        return {player.id_in_group: dict(num_centered=num_centered, bonus=task['bonus'], finished=task['finished'])}

    # Set player fields with number of centered sliders and payoff
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        task = participant.vars['sliders_task']
        player.num_centered = task['num_centered']
        set_excluded_player(player, task['num_centered'])
        if player.excluded:
            participant.pgg_tax_endowment = cu(task['bonus'])

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.excluded and upcoming_apps:
            return upcoming_apps[-1]


page_sequence = [PreRet, SliderTask]