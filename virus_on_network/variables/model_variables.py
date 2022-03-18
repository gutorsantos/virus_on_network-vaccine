from math import inf
from .variables import number_state
from ..states import State

def resistant_susceptible_ratio(model):
    try:
        num_recovered = number_state(model, State.RECOVERED)
        num_susceptibles = number_state(model, State.UNVACCINATED_SUSCEPTIBLE) + number_state(model, State.VACCINATED_SUSCEPTIBLE)
        return  num_recovered / num_susceptibles
    except ZeroDivisionError:
        return inf

def dead_alive(model):
    try:
        num_dead = number_state(model, State.DEAD)
        num_aline = number_state(model, State.UNVACCINATED_SUSCEPTIBLE) + number_state(model, State.VACCINATED_SUSCEPTIBLE)  + number_state(model, State.RECOVERED)
        return num_aline / num_dead
    except ZeroDivisionError:
        return inf