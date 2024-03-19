from game.endless_runner import EndlessRunner
from ai.environment import EndlessRunnerEnv
from stable_baselines3.common.env_checker import check_env

game = EndlessRunner()
env = EndlessRunnerEnv()
# check_env(env, warn=True)


from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env

# Instantiate the env
vec_env = make_vec_env(EndlessRunnerEnv, n_envs=1)