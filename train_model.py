import time
import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.evaluation import evaluate_policy
# monitor wrapper
from stable_baselines3.common.monitor import Monitor

# from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env

# import wandb
# from wandb.integration.sb3 import WandbCallback
# https://docs.wandb.ai/guides/integrations/stable-baselines-3

from reinforcement_learning.environment import EndlessRunnerEnv, TileER, Parrot

from game.util import get_steps
from eval_model import evaluate_model
import random


def train(save_path: str, total_timesteps: float, Env):
    total_timesteps = int(total_timesteps)
    print(f"Saving to [{save_path}] after [{get_steps(total_timesteps)}] timesteps")
    policy_kwargs = dict(activation_fn=th.nn.ReLU, 
                         net_arch=[])  # Empty architecture

    # Stop if model reaches perfect score
    # callback_on_best = StopTrainingOnRewardThreshold(
    #     reward_threshold=Env.max_steps,
    #     verbose=0)

    call_freq = int(total_timesteps / 10**3)  # 10**4 when 10 parallel and t=7
    
    # Evaluate callback
    # eval_callback = EvalCallback(
    #     make_vec_env(Env, 10), 
    #     eval_freq=call_freq, 
    #     # eval_freq=total_timesteps//10, 
    #     verbose=1, 
    #     n_eval_episodes=10,
    #     log_path=save_path,
    #     callback_on_new_best=callback_on_best)
    
    # Checkpoint callback
    checkpoint_callback = CheckpointCallback(
        save_freq=call_freq,
        save_path=save_path,
        name_prefix="",
        verbose=0
        )
    
    callbacks = [checkpoint_callback]
    # callbacks = [eval_callback, checkpoint_callback]

    # Wandb 
    # config = dict(policy="MlpPolicy", 
    #                    total_timesteps=total_timesteps, 
    #                    seed=42, 
    #                    env="EndlessRunner")
    


    # run = wandb.init(project="dda", config=config)
    # wandb_callback = WandbCallback(
    #     gradient_save_freq=config["total_timesteps"]//10,  # Save every 10% of the total timesteps 
    #     model_save_path=save_path,
    #     verbose=2)

    # model = PPO(config["policy"], Env(),
    #             policy_kwargs=policy_kwargs, seed=42)  # Seed for reproducibility
    # model.learn(total_timesteps=config["total_timesteps"], 
    #             callback=[wandb_callback, ProgressBarCallback()])

    env = make_vec_env(Env, 10)  # Main
    # env = Env(render=True)
    
    ppo_seed = random.randint(0, 10**5)
    # ppo_seed = 3144
    model = PPO("MlpPolicy", env,
                policy_kwargs=policy_kwargs, seed=ppo_seed)  # Seed for reproducibility
    print("Learning")
    start = time.time()
    model.learn(total_timesteps=total_timesteps,
            callback=callbacks,
            progress_bar=True)
    print("Saving to", save_path)
    model.save(path=save_path)

    # Final eval
    # mean, std = evaluate_model(save_path, Env)
    with open("logs.csv", "a") as f:
        f.write(f"{save_path}, Full env (less time v4), {get_steps(total_timesteps)}, {time.time() - start:.2f}, {ppo_seed}\n")
        
def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("timesteps", help="Order of magnitude of timesteps. default=4" , type=int, default=4)
    return parser.parse_args()

import numpy as np
from tqdm import tqdm
import os
import csv
from datetime import datetime
def eval(checkpoint_folder):
    # Preparing all players
    all_players = [checkpoint_folder + "/" + f[:-4] for f in os.listdir(checkpoint_folder) if f.endswith(".zip")]
    all_players.sort(key=lambda x: int(x.split("_")[-2]))
    
    # Training session
    print("Evaluating training session")
    means = np.zeros((len(all_players), 10))
    stds = np.zeros_like(means)
    n_episodes = 20
    for i, model_path in enumerate(tqdm(all_players)):
        for j in range(1, 11):
            env = make_vec_env(EndlessRunnerEnv, n_episodes, env_kwargs={"difficulty": (j, 0), "eval": True})
            mean, std = evaluate_policy(PPO.load(model_path), env, n_eval_episodes=n_episodes)
            means[i, j-1] = mean
            stds[i, j-1] = std
    np.save(f"{checkpoint_folder}_train_session", means)
    np.save(f"{checkpoint_folder}_train_session_std", stds)


if __name__ == "__main__":
    t = parse_args().timesteps
    # t = 7
    while True:
        folder = f"models/{datetime.now().strftime("%m_%d/PPO_%H_%M")}"
        print(f"----- TRAINING {folder} -----")
        train(folder, total_timesteps=10**t, Env=EndlessRunnerEnv)
        eval(folder)
    