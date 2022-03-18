import math
from sre_parse import State

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement

from virus_on_network.states import State, StateColor
from virus_on_network.variables.model_variables import dead_alive, resistant_susceptible_ratio
from .model import VirusOnNetwork, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        colors = {
            State.INFECTED: '#FF0000', 
            State.UNVACCINATED_SUSCEPTIBLE: '#ffcc00', 
            State.RECOVERED: '#a6f1f1', 
            State.VACCINATED_SUSCEPTIBLE: '#bdff2e'
        }
        return colors.get(agent.state, "#000000")
            

    def edge_color(agent1, agent2):
        if State.RECOVERED in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if State.RECOVERED in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library="d3")
chart = ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Unvaccinated Susceptible", "Color": "#ffcc00"},
        {"Label": "Vaccinated Susceptible", "Color": "#bdff2e"},
        {"Label": "Recovered", "Color": "#a6f1f1"},
        {"Label": "Dead", "Color": "#000000"},
    ]
)


class MyTextElement(TextElement):
    def render(self, model):
        ratio = resistant_susceptible_ratio(model)
        ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
        infected_text = str(number_infected(model))

        text = ('Resistant/Susceptible Ratio: {}<br> \
                Infected Remaining: {}<br> \
                Alive/Dead Ratio: {}').format(
            ratio_text, infected_text, str(dead_alive(model))
        )

        return text


model_params = {
    "num_nodes": UserSettableParameter(
        "slider",
        "Number of agents",
        10,
        10,
        200,
        1,
        description="Choose how many agents to include in the model",
    ),
    "avg_node_degree": UserSettableParameter(
        "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"
    ),
    "initial_outbreak_size": UserSettableParameter(
        "slider",
        "Initial Outbreak Size",
        1,
        1,
        10,
        1,
        description="Initial Outbreak Size",
    ),
    "virus_spread_chance": UserSettableParameter(
        "slider",
        "Virus Spread Chance",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Probability that susceptible neighbor will be infected",
    ),
    "virus_check_frequency": UserSettableParameter(
        "slider",
        "Virus Check Frequency",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Frequency the nodes check whether they are infected by " "a virus",
    ),
    "recovery_chance": UserSettableParameter(
        "slider",
        "Recovery Chance",
        0.3,
        0.0,
        1.0,
        0.1,
        description="Probability that the virus will be removed",
    ),
    "gain_resistance_chance": UserSettableParameter(
        "slider",
        "Gain Resistance Chance",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
    "vaccinated_rate": UserSettableParameter(
        "slider",
        "Initial Vaccinated Proportion",
        0.5,
        0,
        1,
        0.1,
        description="Set the Initial Vaccinated rate",
    ),
    "vaccine_effectiveness_rate": UserSettableParameter(
        "slider",
        "Vaccine effectiveness rate",
        0.5,
        0,
        1,
        0.01,
        description="Set Vaccine effectiveness rate",
    ),
    "virus_lethality_rate": UserSettableParameter(
        "slider",
        "Virus Lethality",
        0.5,
        0.0,
        1.0,
        0.01,
        description="Probability that infected come to death",
    )
}

server = ModularServer(
    VirusOnNetwork, [network, MyTextElement(), chart], "Virus Model", model_params
)
server.port = 8521
