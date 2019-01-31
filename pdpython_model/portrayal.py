from pdpython_model.agents import PDAgent

def portrayPDAgent(agent):
    """ MESA Suggestion: Portraying agents in their current decision state, for the visualisation """
    assert agent is not None
    # return {
    #     "Shape": "rect",
    #     "w": 1,
    #     "h": 1,
    #     "Filled": "true",
    #     "Layer": 0,
    #     "x": agent.pos[0],
    #     "y": agent.pos[1],
    #     "Color": "green" if agent.isCooroperating else "red"  # This will need to be altered when we start
    #     # diversifying behaviour
    # }  ^ this could be a more streamlined way of putting it, I'm not so familiar with @properties tho

    portrayal = {}

    if type(agent) is PDAgent:
        if agent.strategy == "ANGEL":
            portrayal["Color"] = "yellow"
            portrayal["text"] = agent.move, agent.score
        elif agent.strategy == "DEVIL":
            portrayal["Color"] = ["red", "black"]
            portrayal["text"] = agent.move, agent.score

        if agent.move == None:
            return
        # THIS NEEDS TO GO ON AND SO ON FOR EACH STRATEGY
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

