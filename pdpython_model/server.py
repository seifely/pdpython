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
                         "Color": "white",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "black",
                         "scale": 1
                         }
        elif agent.strategy == "ANGEL":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#ffe700",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#f08619",
                         "scale": 1
                         }
        elif agent.strategy == "DEVIL":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#d52719",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#3e0400",
                         "scale": 1
                         }
        elif agent.strategy == "EV":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#84f2cf",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#09806b",
                         "scale": 1
                         }
        elif agent.strategy == "RANDOM":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "grey",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "white",
                         "scale": 1
                         }
        elif agent.strategy == "VEV":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#008080",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#84f2cf",
                         "scale": 1
                         }
        elif agent.strategy == "TFT":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#ffd0ef",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#f57694",
                         "scale": 1
                         }
        elif agent.strategy == "WSLS":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#add8e6",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "blue",
                         "scale": 1
                         }
        elif agent.strategy == "VPP":
            portrayal = {"Shape": "circle",
                         "scale": 1,
                         "Color": "#003333",
                         "Filled": "true",
                         "Layer": 1,
                         "r": 0.75,
                         "text": [agent.common_move, agent.score],
                         "text_color": "#99cccc",
                         "scale": 1
                         }

    return portrayal


canvas_element = CanvasGrid(gen_Model_Portrayal, 8, 8, 500, 500)
# chart_element = ChartModule([{"Label": "Walkers", "Color": "#AA0000"},
#                              {"Label": "Closed Boxes", "Color": "#666666"}])

model_params = {"number_of_agents": UserSettableParameter('slider', 'Number of Agents', 2, 2, 64, 1),
                "collect_data": UserSettableParameter('checkbox', 'Collect Data', False),
                "agent_printing": UserSettableParameter('checkbox', 'Agent Printouts', False)
                }

server = ModularServer(PDModel, [canvas_element], "Generic Model", model_params)
server.port = 8521
