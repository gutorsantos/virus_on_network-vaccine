from .variables import number_state
from ..states import State

# Get the number of infected
def number_infected(model):
    return number_state(model, State.INFECTED)

# Get the number of unvaccinated
def number_unvaccinated_susceptible(model):
    return number_state(model, State.UNVACCINATED_SUSCEPTIBLE)

# Get the number of vaccinated
def number_vaccinated_susceptible(model):
    return number_state(model, State.VACCINATED_SUSCEPTIBLE)

# Get the number of susceptibles
def number_susceptibles(model):
    return number_unvaccinated_susceptible(model) + number_vaccinated_susceptible(model)

# Get the number of recovered
def number_recovered(model):
    return number_state(model, State.RECOVERED)

# Get the number of dead
def number_dead(model):
    return number_state(model, State.DEAD)