# pdpython
PhD Thesis Project on the Prisoner's Dilemma, implemented in Python 3.6

This project contains scripting using the Python library MESA (https://mesa.readthedocs.io/en/stable/) for simulating agents playing the Repeated Prisoner's Dilemma in a grid environemt.

UPDATE 10/05/21: The Master branch should be up to date with the latest running version, including running instructions (see the .pptx file)  and the single-test visualiser.

TODO: 

# To Run Locally

- Ensure python is installed.
- Install the necessary libraries: mesa (pip install mesa), numpy and scipy (pip install numpy scipy), pandas (pip install pandas)
- If primarily testing standard SARSA agents against a variety of opponents, set the batch_run.py 'sarsa_spawn', 'sarsa_training' and 'sarsa_testing' variables to True 
- [CURRENTLY] Change the simulation variables in batch_run.py at the bottom of the script - br_params - so that uncommented lists contain the variable values wished to test
- [CURRENTLY] Change the csv filename variable around line 540 (in the batchrunner) to a desired string, leaving the %s string replacements as is
- run the batch_run.py file to begin data collection

- By default, the simulation will run a 5x5 grid of 25 agents, and as long as the sarsa_distro variable is left untouched, these agents will spawn in a 'checkerboard' formation, where SARSA agents are pitted off against each strategy listed in the 'sarsa_oppo' br_params list

ALTERNATIVELY: There are instructions on how to run things in the .pptx file included in master.

# Opponent Strategy Codes

- 'TFT' - Tit for Tat
- 'WSLS' - Win-Stay Lose-Shift
- 'DEVIL' - All-defectors
- 'ANGEL' - All-cooperators
- 'RANDOM' - Self-evident
- 'VPP' - Variable Personal Probability, a novel strategy designed by us that updates its probabilistic likelihood of defection incrementally based on observed behaviour
- 'LEARN' - The on-policy reinforcment learning algorithm, state-action-reward-state-action
- 'MOODYLEARN' - The moody version, adapted from [1]


[1] http://cognet.mit.edu/proceed/10.7551/ecal_a_021
