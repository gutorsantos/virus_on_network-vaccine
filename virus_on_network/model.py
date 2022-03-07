import math
from enum import Enum
import networkx as nx

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from mesa.batchrunner import BatchRunner
from datetime import datetime


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    SUSCEPTIBLE_AND_VACCINATED = 4


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)

def number_vaccinated(model):
    return number_state(model, State.SUSCEPTIBLE_AND_VACCINATED)


class VirusOnNetwork(Model):
    '''A virus model with some number of agents'''

    def __init__(
        self,
        num_nodes=10,
        avg_node_degree=3,
        initial_outbreak_size=1,
        virus_spread_chance=0.4,
        virus_check_frequency=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.5,
        num_vaccinated=10,
        vaccine_rate=0.5
    ):

        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

        self.num_vaccinated = num_vaccinated
        self.vaccine_rate = vaccine_rate

        self.datacollector = DataCollector(
            {
                'Infected': number_infected,
                'Susceptible': number_susceptible,
                'Resistant': number_resistant,
                'Susceptible and Vaccinated': number_vaccinated
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(
                i,
                self,
                State.SUSCEPTIBLE,
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.recovery_chance,
                self.gain_resistance_chance,
                self.vaccine_rate
            )
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        # Vaccinate some nodes
        infected_nodes = self.random.sample(self.G.nodes(), math.floor(self.num_nodes * self.num_vaccinated))
        for a in self.grid.get_cell_list_contents(infected_nodes):
            if a.state != State.INFECTED:
                a.state = State.SUSCEPTIBLE_AND_VACCINATED
                a.vaccine_rate = self.vaccine_rate

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class VirusAgent(Agent):
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        recovery_chance,
        gain_resistance_chance,
        vaccine_rate
    ):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.vaccine_rate=vaccine_rate

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE or agent.state is State.SUSCEPTIBLE_AND_VACCINATED
        ]
        for a in susceptible_neighbors:
            if a.state == State.SUSCEPTIBLE:
                if self.random.random() < self.virus_spread_chance:
                    a.state = State.INFECTED
            elif a.state == State.SUSCEPTIBLE_AND_VACCINATED:
                t = self.random.random()
                b = abs(self.virus_spread_chance*(1-self.vaccine_rate))
                print(t, b)
                if t < abs(self.virus_spread_chance*(1-self.vaccine_rate)):
                    a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self, initial_state):
        # Try to remove
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = initial_state#State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self, initial_state):
        if self.random.random() < self.virus_check_frequency:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection(initial_state)

    def step(self):
        initial_state = self.state
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation(initial_state)

def batch_run():
    fixed_params = {
        'avg_node_degree': 10,
        'virus_check_frequency': 0.4,
        'gain_resistance_chance': 0.5,
        'recovery_chance': 0.3,

    }

    variable_params = {
        'num_nodes': [10, 20, 40, 100],
        'initial_outbreak_size': [1],
        'virus_spread_chance': [0.9, 0.7, 0.5],
        'num_vaccinated': [0, 0.1, 0.25, 0.5, 0.8],
        'vaccine_rate': [0.5, 0.8, 0.95]
    }

    experiments_per_parameter_configuration = 10
    max_steps_per_simulation = 10
    
    batch_run = BatchRunner(
        VirusOnNetwork,
        variable_params,
        fixed_params,
        iterations=experiments_per_parameter_configuration,
        max_steps=max_steps_per_simulation,
        model_reporters = {
            'Infected': number_infected,
            'Susceptible': number_susceptible,
            'Resistant': number_resistant,
            'Susceptible and Vaccinated': number_vaccinated
        },
        agent_reporters = {
            'State': 'vaccine_rate'
        }
    )
    batch_run.run_all()

    run_model_data = batch_run.get_model_vars_dataframe()
    run_agent_data = batch_run.get_agent_vars_dataframe()

    now = str(datetime.now())
    file_name_suffix =  ('_iter_'+str(experiments_per_parameter_configuration)+
                        '_steps_'+str(max_steps_per_simulation)+'_'+
                        now)
    run_model_data.to_csv('model_data'+file_name_suffix+'.csv')
    run_agent_data.to_csv('agent_data'+file_name_suffix+'.csv')