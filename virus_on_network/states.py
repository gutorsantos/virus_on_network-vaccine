from enum import Enum

class State(Enum):
    UNVACCINATED_SUSCEPTIBLE = 0
    VACCINATED_SUSCEPTIBLE = 1
    INFECTED = 2
    RECOVERED = 3
    DEAD = 4

class StateColor(Enum):
    UNVACCINATED_SUSCEPTIBLE = '#ffcc00'
    VACCINATED_SUSCEPTIBLE = '#bdff2e'
    INFECTED = '#FF0000'
    RECOVERED = '#a6f1f1'
    DEAD = '#000000'
