from ast import Return
import math
from random import random
import networkx as nx
import numpy as np

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from mesa.batchrunner import BatchRunner
from datetime import datetime

from .states import State

# Import methods to get variables
from .variables.model_variables import *
from .variables.agent_variables import *

from .calculate_normal import calculate_normal

class VirusOnNetwork(Model):
    '''A virus model with some number of agents'''

    def __init__(
        self,
        num_nodes,
        avg_node_degree,
        initial_outbreak_size,
        virus_spread_chance,
        recovery_chance,
        vaccinated_rate,
        vaccine_effectiveness_rate,
        virus_lethality_rate
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
        self.recovery_chance = recovery_chance

        self.vaccinated_rate = vaccinated_rate
        self.vaccine_effectiveness_rate = vaccine_effectiveness_rate
        self.virus_lethality_rate = virus_lethality_rate

        self.datacollector = DataCollector(
            {
                'Infected': number_infected,
                'Unvaccinated Susceptible': number_unvaccinated_susceptible,
                'Vaccinated Susceptible': number_vaccinated_susceptible,
                'Recovered': number_recovered,
                'Dead': number_dead
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(
                i,
                self,
                State.UNVACCINATED_SUSCEPTIBLE,
                self.virus_spread_chance,
                self.recovery_chance,
                self.vaccine_effectiveness_rate,
                self.virus_lethality_rate
            )
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        # Vaccinate some nodes
        infected_nodes = self.random.sample(self.G.nodes(), math.floor(self.num_nodes * self.vaccinated_rate))
        for a in self.grid.get_cell_list_contents(infected_nodes):
            if a.state != State.INFECTED:
                a.state = State.VACCINATED_SUSCEPTIBLE
                a.initial_set_state = State.VACCINATED_SUSCEPTIBLE
                a.vaccine_effectiveness_rate = self.vaccine_effectiveness_rate

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()

ASSYMPTOMATIC_INFECTED_PERIOD = 2
MAX_INFECTION_PERIOD = 15
SYMPTOMATIC_PERIOD = 3
# in this model we are simulating a virus that can only infect when symptoms begin

class VirusAgent(Agent):
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        recovery_chance,
        vaccine_effectiveness_rate,
        virus_lethality_rate
    ):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.recovery_chance = recovery_chance
        self.vaccine_effectiveness_rate=vaccine_effectiveness_rate
        self.virus_lethality_rate = virus_lethality_rate
        self.days_infected = 0
        self.initial_set_state = initial_state

    def try_to_infect_neighbors(self):
        # there is no sufficent viral charge
        if(self.days_infected < ASSYMPTOMATIC_INFECTED_PERIOD+1):
            return
        if(self.days_infected > 15):
            return
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.UNVACCINATED_SUSCEPTIBLE or agent.state is State.VACCINATED_SUSCEPTIBLE
        ]

        # a unvaccinated person is more susceptible to get infected
        for a in susceptible_neighbors:
            if a.state == State.UNVACCINATED_SUSCEPTIBLE:
                if self.random.random() < self.virus_spread_chance:
                    a.state = State.INFECTED
            elif a.state == State.VACCINATED_SUSCEPTIBLE:
                random = self.random.random()
                reduced_chance = self.virus_spread_chance*(1-self.vaccine_effectiveness_rate)
                if random < reduced_chance:
                    a.state = State.INFECTED

    def try_remove_infection(self):
        # impossible to recover in 3 days
        if(self.days_infected < ASSYMPTOMATIC_INFECTED_PERIOD+1):
            return False

        if self.random.random() < self.recovery_chance:
            # Success
            self.state = State.RECOVERED
            return True
        return False

    def death(self):
        if(self.days_infected < ASSYMPTOMATIC_INFECTED_PERIOD+1):
            return False
        if(self.days_infected > 15):
            return False

        prob = calculate_normal(self.days_infected)
        death_chance = prob/4 if self.initial_set_state == State.VACCINATED_SUSCEPTIBLE else prob
        random = self.random.random()

        if random < death_chance:
            self.state = State.DEAD
            return True
        
        return False

    def try_check_situation(self):
        if(not self.death()):
            self.try_remove_infection()
                
                    

    def step(self):
        if self.state is State.INFECTED:
            self.days_infected = self.days_infected + 1
            self.try_to_infect_neighbors()
            self.try_check_situation()

def batch_run():
    fixed_params = {
        'avg_node_degree': 10,
        'recovery_chance': 0.3,
        'num_nodes': 1000,
        'initial_outbreak_size': 1,
        'virus_spread_chance': 0.9,
        'vaccine_effectiveness_rate': 0.9,
        'virus_lethality_rate': 0.2
    }

    variable_params = {
        'vaccinated_rate': [0, 0.1, 0.5, 0.7, 0.9],
    }

    experiments_per_parameter_configuration = 300
    max_steps_per_simulation = 50
    
    batch_run = BatchRunner(
        VirusOnNetwork,
        variable_params,
        fixed_params,
        iterations=experiments_per_parameter_configuration,
        max_steps=max_steps_per_simulation,
        model_reporters = {
            'Resistant Susceptible Ratio': resistant_susceptible_ratio,
            'Alive Dead Ratio': alive_per_death,
            'Mortality': mortality,
            'Infected': number_infected,
            'Unvaccinated Susceptible': number_unvaccinated_susceptible,
            'Vaccinated Susceptible': number_vaccinated_susceptible,
            'Recovered': number_recovered,
            'Dead': number_dead
        },
        agent_reporters = {
            'State': 'state'
        }
    )
    # run
    batch_run.run_all()

    # collect data
    run_model_data = batch_run.get_model_vars_dataframe()
    run_agent_data = batch_run.get_agent_vars_dataframe()

    # csv file name
    now = str(datetime.now())
    file_name_suffix =  ('_iter_'+str(experiments_per_parameter_configuration)+
                        '_steps_'+str(max_steps_per_simulation)+'_'+
                        now)
    run_model_data.to_csv('model_data'+file_name_suffix+'.csv')
    run_agent_data.to_csv('agent_data'+file_name_suffix+'.csv')