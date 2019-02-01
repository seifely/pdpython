from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from pdpython_model.agents import PDAgent
from pdpython_model.model import PDModel


def gen_Model_Portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is PDAgent:
        if agent.strategy is None:
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "black",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.5,
                         "text": [agent.move, " ", agent.score],
                         "text_color": "white",
                         "scale": 1
                         }
        elif agent.strategy == "ANGEL":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "yellow",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.5,
                         "text": [agent.move, " ", agent.score],
                         "text_color": "black",
                         "scale": 1
                         }
        if agent.strategy == "DEVIL":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "red",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.5,
                         "text": [agent.move, " ", agent.score],
                         "text_color": "white",
                         "scale": 1
                         }
        if agent.strategy == "FP":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "green",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.5,
                         "text": [agent.move, " ", agent.score],
                         "text_color": "white",
                         "scale": 1
                         }

    return portrayal

canvas_element = CanvasGrid(gen_Model_Portrayal, 5, 5, 500, 500)
# chart_element = ChartModule([{"Label": "Walkers", "Color": "#AA0000"},
#                              {"Label": "Closed Boxes", "Color": "#666666"}])

model_params = {"number_of_agents": UserSettableParameter('slider', 'Number of Agents', 2, 2, 25, 1),
                }

server = ModularServer(PDModel, [canvas_element], "Generic Model", model_params)
server.port = 8521
