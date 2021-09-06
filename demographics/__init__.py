from otree.api import *


doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'demographics'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

############################### DEMOGRAPHICS ######################
class Player(BasePlayer):
    age = models.IntegerField(label="Indichi la Sua età", min=18, max=99)
    gender = models.StringField(label="Qual è il Suo genere?",
                                choices=['Maschio', 'Femmina', 'Altro', 'Preferisco non specificare']
                                )
    occupationalstatus = models.StringField(label="Qual è attualmente la Sua posizione lavorativa?",
                                            choices=['Occupata/o autonoma/o', 'Imprenditrice/imprenditore',
                                                     'Occupata/o dipendente pubblico',
                                                     'Occupata/o dipendente privato', 'Pensionata/o', 'Studente(ssa)',
                                                     'Disoccupata/o', 'Inattiva/o']
                                            )

    regions = models.StringField(label="In quale regione italiana è nata/o?",
                                 choices=['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia Romagna',
                                          'Friuli Venezia Giulia', 'Lazio',
                                          'Liguria', 'Lombardia', 'Marche', 'Molise', 'Piemonte',
                                          'Provincia Autonoma di Bolzano',
                                          'Provincia Autonoma di Trento', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
                                          'Umbria', 'Valle dAosta',
                                          'Veneto']
                                 )


# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'occupationalstatus', 'regions']

page_sequence = [Demographics]
