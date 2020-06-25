import random


def init_qtable(states, n_actions):
    iqtable = {}   # does this want to be a list or a dict?

    for i in states:
        indx = tuple(i)
        vu = []
        for j in range(n_actions):
            vu.append(random.uniform(0.0, 1.0))
        iqtable[indx] = vu

    return iqtable


def egreedy_action(e, qtable, current_state):
    """ Qtable should be a dict keyed by the states - tuples of 7 values. """

    p = random.random()

    if p < e:
        return random.choice(['C', 'D'])
    else:
        # index qtable by current_state
        current = qtable[current_state]
        # pick the action with the highest Q value - if indx:0, C, if indx:1, D
        if current[0] > current[1]:
            return 'C'
        else:  # this might need to be an elif, but with two behaviours it's fine
            return 'D'


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

def update_epsilon(initial, current, max_round, linear):
    # Version WITHOUT simulated annealing, though that could be in V2
    if linear:
        increment = initial / max_round
        new_epsilon = current - increment
        return new_epsilon
    else:
        increment = current / 50        # any better value to use rather than arbitrary?
        new_epsilon = current - increment
        return new_epsilon


def update_q(reward, gamma, alpha, oldQ, nextQ):
    """ Where nextQ is determined by the epsilon greedy choice that has already been made. """

    newQ = oldQ + alpha * (reward + ((gamma*nextQ) - oldQ))

    return newQ


# to integrate SVO into sarsa, we could try two methods
# a: weight the value of rewards received in each state my your orientation
