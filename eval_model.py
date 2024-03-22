import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env

from reinforcement_learning.environment import EndlessRunnerEnv, DumbEnv

if __name__ == "__main__":
    endless = 1
    if endless:
        path = "models/03_20/PPO_17_34.zip"     # R(86.00, 142.63)
        # path = "models/Random.zip"            # R(-0.10, 27.52)
        Env = EndlessRunnerEnv 
    else:
        path = "models/03_21/Dumb_09_43.zip"
        Env = DumbEnv
    model = PPO.load(path)
    model.set_env(Env())

    mean, std = evaluate_policy(
        model, 
        model.get_env(),
        n_eval_episodes=10
        )
    
    print(f"R({mean:.2f}, {std:.2f})")
    model.get_env().close()









