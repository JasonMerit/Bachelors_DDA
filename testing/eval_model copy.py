import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env

from reinforcement_learning.environment import EndlessRunnerEnv, DumbEnv

"""This script answers which is the fastest way to evaluate a model"""

def eval_policy(model: PPO, n_episodes=10):
    mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=n_episodes)
    print(f"R({mean_reward:.2f}, {std_reward:.2f})")
    model.get_env().close()

def jason(model: PPO, env: EndlessRunnerEnv, n_episodes=10):
    """Single env, not parallelized"""
    # env = model.get_env()
    obs, _ = env.reset()  # Seed for reproducibility
    rewards = np.zeros(n_episodes)
    done = False
    for episode in range(n_episodes):
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, term, trunc, _ = env.step(action)
            rewards[episode] += reward
            done = term or trunc
        obs, _ = env.reset()
        done = False
    
    print(f"R({np.mean(rewards):.2f}, {np.std(rewards):.2f})")

def jason1(model: PPO, Env, n_episodes=10):
    """vec env but only one env is used, so it's not parallelized"""
    env = make_vec_env(Env)
    obs = env.reset()  # Seed for reproducibility
    rewards = np.zeros(n_episodes)
    done = False
    for episode in range(n_episodes):
        while not done:
            action, _ = model.predict(obs[0], deterministic=True)
            obs, reward, done, _ = env.step([action])
            rewards[episode] += reward[0]
        obs = env.reset()
        done = False
                
    print(f"R({np.mean(rewards):.2f}, {np.std(rewards):.2f})")

def jason2(model: PPO, Env, n_episodes=10):
    """Fucked, because done environments reset"""
    env = make_vec_env(Env, n_episodes)
    obs = env.reset()  # Seed for reproducibility
    done = [False] * n_episodes
    while False in done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _ = env.step(action)
    rewards = np.sum(reward, axis=0)
    print(f"R({np.mean(rewards):.2f}, {np.std(rewards):.2f})")

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
    model.set_env(Env(True))

    from game.util import end
    end()
    
    # eval_policy(model, 10)
    # end()
    jason(model, Env(), 10)  # R(86.00, 142.63)
    end()
    # jason1(model, Env, 10)
    # end()
    # jason2(model, Env, 10)
    # end()









