import random
import math

def observe_state(obsAction, oppID, oppMood, stateMode):
    """Keeping this as a separate method in case we want to manipulate the observation somehow,
    like with noise (x chance we make an observational mistake, etc)."""
    state = []
    if stateMode == 'stateless':
        state.append(obsAction)
    elif stateMode == 'agentstate':
        state.append(obsAction)
        state.append(oppID)
    elif stateMode == 'moodstate':
        state.append(obsAction)
        state.append(oppID)
        state.append(oppMood)
    # Returns a list, but this should be utilised as a tuple when used to key a Q value
    return state

def init_qtable(states, n_actions, zeroes):
    """First value is for cooperate, second value is for defect."""
    iqtable = {}   # does this want to be a list or a dict?

    for i in states:
        indx = tuple(i)
        vu = []
        for j in range(n_actions):
            if zeroes:
                vu.append(0)
            else:
                vu.append(random.uniform(0.0, 1.0))

        #print('indx=', indx, 'vu=', vu)
        iqtable[indx] = vu
    return iqtable


def moody_action(mood, state, qtable, moodAffectMode, epsilon, moodAffect):
    """ Fixed Amount should be in the model as a test parameter MA """
    change = epsilon  # not sure why change is set to epsilon to start with --> in case none of the loops take effect
    # TODO: part of this function needs to produce an altered epsilon value
    epsChange = 0  # this should stay at no change if mood isn't high or low

    r = random.randint(1, 100) / 100  # Still not sure about this line and below, it might need to be if r > 50?
    if r > 0:
        todo = 'C'
    else:
        todo = 'D'
    # Inititally starts with cooperation

    # index qtable by current state
    current = qtable[tuple(state)]
    if current[1] > current[0]:
        if mood > 70 and moodAffectMode == 'Fixed':
            change = moodAffect
            epsChange = change
        elif mood > 70 and moodAffectMode == 'Mood':
            change = ((mood - 50) / 100)
            epsChange = change

        if r > (1-change):  # because change is epsilon, this section is the e-greedy choice making
            todo = 'D'
        else:
            todo = 'C'

    elif current[0] > current[1]:
        if mood < 30 and moodAffectMode == 'Fixed':
            change = moodAffect
            epsChange = change
        elif mood < 30 and moodAffectMode == 'Mood':
            change = ((50 - mood) / 100)
            epsChange = change

        if r < (1-change):
            todo = 'C'
        else:
            todo = 'D'

    newEps = epsilon + epsChange
    return todo, newEps

def getMoodType(mood):
    if mood > 70:
        return 'HIGH'
    elif mood < 30:
        return 'LOW'
    else:
        return 'NEUTRAL'

# def egreedy_action(e, qtable, current_state, paired):
#     """ Qtable should be a dict keyed by the states - tuples of 7 values. """
#
#     p = random.random()
#
#     if p < e:
#         return random.choice(["C", "D"])
#     else:
#         # index qtable by current_state
#         if len(current_state) == 1:
#             if paired:
#                 current_state = current_state[0]
#         # print('my state:', current_state)
#         # print("q", qtable)
#         current = qtable[tuple(current_state)]
#         # print('qvalues:', current)
#         # pick the action with the highest Q value - if indx:0, C, if indx:1, D
#         if current[0] > current[1]:
#             return "C"
#         elif current[1] > current[0]:  # this might need to be an elif, but with two behaviours it's fine
#             return "D"
#         else:
#             return random.choice(["C", "D"])


def sarsa_decision(alpha, epsilon, gamma):
    # initialise q table
    # choose action
    # observe reward and the resulting state (S') (check partner, new state)
    # output the next action we should take using egreedy and the next projected state
    # after action staged, in the
    return

def output_sprime(current_state, observed_action):
    """ Returns a tuple that adds the observed action to the stack. Current state should be a tuple of strings?"""
    cstate = list(current_state)
    cstate.pop(0)
    cstate.append(observed_action)
    return tuple(cstate)

def decay_value(initial, current, max_round, linear, floor):
    # Version WITHOUT simulated annealing, though that could be in V2
    if linear:
        increment = initial / max_round
        new_value = current - increment
        if new_value < floor:
            if floor > 0:
                return floor
            else:
                return new_value
        else:
            return new_value
    else:
        increment = current / 50        # any better value to use rather than arbitrary?
        new_value = current - increment
        if new_value > floor:
            return floor
        else:
            return new_value

def update_q(step_number, actionTaken, state, qtable, payoff, memory, currMood):
    # TODO: Need to manage memory outside of this function, as we do with working memory /
    # TODO: Needs to be a NEW memory of payoffs gained instead of moves observed
    """THIS RETURNS UPDATED Q VALUES FROM OLD Q VALUES"""
    current = qtable[tuple(state)]
    if step_number is not None:
        if step_number is not 0:
            if actionTaken == 'C':
                current[0] = learn(current[0], payoff, memory, currMood)
                return current[0], current[1]
            else:
                current[1] = learn(current[1], payoff, memory, currMood)
                return current[0], current[1]
        else:
            if actionTaken == 'C':
                current[0] = payoff
                current[1] = 0
                return current[0], current[1]
            else:
                current[0] = 0
                current[1] = payoff
                return current[0], current[1]
    else:
        if actionTaken == 'C':
            current[0] = payoff
            current[1] = 0
            return current[0], current[1]
        else:
            current[0] = 0
            current[1] = payoff
            return current[0], current[1]


# def update_q(reward, gamma, alpha, oldQ, nextQ):
#     """ Where nextQ is determined by the epsilon greedy choice that has already been made. """
#
#     newQ = oldQ + alpha * (reward + ((gamma*nextQ) - oldQ))
#     return newQ
#

def learn(oldQ, reward, memory, mood):
    newQ = oldQ + 0.1 * (reward + (0.95*estimateFutureRewards(mood, memory)) - oldQ)
    return newQ

def estimateFutureRewards(mood, memory):
    percentToLookAt = (100 - mood) / 100
    actualAmount = math.ceil((len(memory) * percentToLookAt))

    tot = sum(memory[0:actualAmount+1])
    return tot/actualAmount


def update_mood(currentmood, score, averageScore, oppScore, oppAverage):
    ab = (100 - currentmood) / 100
    u = averageScore - ((ab * max((oppAverage - averageScore), 0)) - (ab * max((averageScore - oppAverage), 0)))
    dif = score - u

    newMood = min(99.999, (currentmood + dif))
    newMood = max(0.0001, newMood)
    return newMood


def get_payoff(myMove, oppMove, CCpayoff, DDpayoff, CDpayoff, DCpayoff):
    outcome = [myMove, oppMove]

    if outcome == ['C', 'C']:
        return CCpayoff
    elif outcome == ['C', 'D']:
        return CDpayoff
    elif outcome == ['D', 'C']:
        return DCpayoff
    else:
        return DDpayoff


# to integrate SVO into sarsa, we could try two methods
# a: weight the value of rewards received in each state my your orientation
