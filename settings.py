from os import environ

SESSION_CONFIGS = [
    dict(
        name='ret_slider',
        app_sequence=['ret_slider'],
        num_demo_participants=1,
        ret_slider_num=10,
        ret_slider_ncols=2,
        bonus_per_slider=10
    ),
    dict(
        name='pgg_tax_info',
        display_name='Tax Game - Si Info',
        app_sequence=['instr','pgg_tax', 'results'],
        num_demo_participants=8,
        info=True
    ),
    dict(
        name='pgg_tax_no_info',
        display_name='Tax Game - No Info',
        app_sequence=['instr', 'pgg_tax', 'results'],
        num_demo_participants=8,
        info=False
    ),
    dict(
        name='risk_eg',
        display_name='Risk - Eckel and Grossman 2002',
        app_sequence=['risk_eg'],
        num_demo_participants= 2,
    ),
    dict(
        name='svo',
        display_name='SVO Chris oTree',
        app_sequence=['svo'],
        num_demo_participants= 1,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['pgg_tax_endowment', 'excluded', 'dropout', 'round_to_pay', 'payoff_to_pay', 'svo_angle','svo_category']
SESSION_FIELDS = ['sliders_task_pms']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4221376580418'
