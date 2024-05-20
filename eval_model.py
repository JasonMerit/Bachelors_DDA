import numpy as np
from time import time
from tqdm import tqdm

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecEnv, SubprocVecEnv

from reinforcement_learning.agent import CheaterAgent
from reinforcement_learning.environment import EndlessRunnerEnv

def rollout(env: EndlessRunnerEnv, model: PPO):
    obs, _ = env.reset()
    done = False
    score = 0
    
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, term, trunc, _ = env.step(action)
        done = term or trunc
        score += reward
    return score

def evaluate_model(model_path: str, Env, difficulty=None, n_episodes: int = 50):
    if difficulty is None:
        ## Stratify across difficulty
        means = [0.0] * 10
        stds = [0.0] * 10
        assert n_episodes % 10 == 0, "n_episodes must be divisible by 10 to stratify across difficulty."
        n_episodes = n_episodes // 10
        for d in range(10):
            env = make_vec_env(Env, n_episodes, env_kwargs={"difficulty": (d+1, 0)})
            mean, std = evaluate_policy(PPO.load(model_path), env, n_eval_episodes=n_episodes)
            means[d], stds[d] = mean, std
        return np.mean(means), np.mean(stds)
    
    env = make_vec_env(Env, n_episodes, env_kwargs={"difficulty": difficulty})
    mean, std = evaluate_policy(PPO.load(model_path), env, n_eval_episodes=n_episodes)
    return mean, std

def evaluate_model_jason(model_path: str, Env, difficulty=None, n_episodes: int = 50):
    scores = np.zeros(n_episodes)
    model = PPO.load(model_path)
    # env = Env(difficulty=difficulty)
    env = Env(difficulty=difficulty, render=True)
    for i in tqdm(range(n_episodes)):
        scores[i] = rollout(env, model)
    return scores

import os
def evaluate_training_session(training_path: str, Env):
    # Get all models in training session
    models = [f[:-4] for f in os.listdir(training_path) if f.endswith(".zip")]
    for model in tqdm(models):
        mean, std = evaluate_model(f"{training_path}/{model}", Env)
        # continue if already contained
        with open(f"{training_path}_train_evals.csv", "a") as f:
            # if model in f.read():
            #     continue
            f.write(f"{model},{mean:.2f},{std:.2f}\n")

import matplotlib.pyplot as plt
import csv
def prepare_data(data_path):
    data = []
    with open(data_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            run = row[0]
            run = int(run[1:run.rfind("_")])
            data.append((run, float(row[1]), float(row[2])))
    
    data.sort(key=lambda x: x[0])  # Unsorted for some reason?
    return data

def plot_scores(data_path):
    data = prepare_data(data_path)
    # plot it with errorbars
    # xx = [d[0] for d in data]
    y = [d[1] for d in data]
    e = [d[2] for d in data]
    plt.errorbar(range(len(y)), y, e, ecolor='r', capsize=3)
    plt.title(f"Training Progress of {data_path[:-4]}")
    plt.xlabel("Training Run [1e5]")
    plt.ylabel("Mean Reward")
    # with open("models/04_14/PPO_07_08_train_evals_.csv", "w") as f:
    #     for d in data:
    #         f.write(f"{d[0]},{d[1]},{d[2]}\n")
    plt.show()
    
    # print top 3, bottom 3 and median 3
def print_contenders(data):
    data.sort(key=lambda x: x[1])
    low, mid, high = data[:3], data[len(data)//2 - 1:len(data)//2 + 2], data[-3:]
    print("Bottom 3")
    for i in range(3):
        print(data[i])
    print("Median 3")
    for i in range(3):
        print(data[len(data)//2 - 1 + i])
    print("Top 3")
    for i in range(3):
        print(data[-1-i])

    # Lowest std
    low = low[np.argmin(np.array(low)[:, 2])][0]
    mid = mid[np.argmin(np.array(mid)[:, 2])][0]
    high = high[np.argmin(np.array(high)[:, 2])][0]
    print(f'players = ["{low}", "{mid}", "{high}"]')

def print_missing(xx):
    last = 0
    for x in xx:
        val = int(x // 1e5)
        if val - last != 1:
            print(f"Missing {last+1} to {val-1}")
        last = val

def create_difficulty_matrix(player: str, tag=""):
    for i in range(1, 11):
        for j in range(1, 11):
            mean, std = evaluate_model(player, EndlessRunnerEnv, difficulty=(i, j), n_episodes=50)
            with open(f"{player}_diff_mat{tag}.csv", "a") as f:
                f.write(f"{i}, {j}, {mean:.2f}, {std:.2f}\n")

def plot_difficulty_matrix(data_path: str, title=None):
    # if not os.path.exists(data_path):
    #     create_ndarray(data_path, data_path)
    # else:
    data = np.load(data_path)
    # flip y axis of data
    data = np.flip(data, axis=0)
    plt.matshow(data, extent=(1, 10, 1, 10))
    plt.xlabel('P(death)')
    plt.ylabel("\u0394gap")
    plt.title(title if title is not None else "Difficulty Matrix")
    plt.colorbar()
    plt.show()

def subplot_difficulty_matrix(
        players: list[str], 
        titles=["Low", "Mid", "High"], 
        share_cbar=False):

    fig, axs = plt.subplots(1, len(players), figsize=(15, 5))
    extent = (1, 11, 1, 11)
    extent = [e - 0.5 for e in extent]

    best = players[-1]
    data = np.load(f"{best}_means.npy")
    vmax = data.max()

    for i, ax in enumerate(axs):
        data_path = f"{players[i]}_means.npy"
        data = np.load(data_path)
        if i == 0:
            vmin = data.min()
        data = np.flip(data, axis=0)
        if not share_cbar:
            im = ax.matshow(data, extent=extent)
            ax.figure.colorbar(ax.images[0], ax=ax, orientation='vertical')
        else:
            im = ax.matshow(data, extent=extent, vmin=vmin, vmax=vmax)
        ax.set_xlabel("P(death)")
        ax.set_ylabel("\u0394gap")
        ax.xaxis.set_ticks_position('bottom')
        # show all ticks
        ax.set_xticks(range(1, 11))
        ax.set_yticks(range(1, 11))
        ax.set_title(f"{titles[i]}")
    if share_cbar:
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        fig.colorbar(im, cax=cbar_ax)
    plt.show()

def subplot_all(players, rows, cols):
    _, axs = plt.subplots(rows, cols, figsize=(15, 5))
    extent = (1, 11, 1, 11)
    extent = [e - 0.5 for e in extent]

    for i, ax in enumerate(axs.flat):
        data = np.load(f"{players[i]}_means.npy")
        data = np.flip(data, axis=0)
        ax.matshow(data, extent=extent)
        # ax.set_xlabel("P(death)")
        # ax.set_ylabel("\u0394gap")
        ax.xaxis.set_ticks_position('bottom')
        # show all ticks
        ax.set_xticks(range(1, 11))
        ax.set_yticks(range(1, 11))
        ax.figure.colorbar(ax.images[0], ax=ax, orientation='vertical')
        ax.set_title(f"{players[i][24:-6]}")    
    plt.show()
    
def create_ndarray(player:str, std=False):
    col = 3 if std else 2

    with open(f"{player}_diff_mat.csv", "r") as f:
        reader = csv.reader(f)
        matrix = np.zeros((10, 10))
        for row in reader:
            matrix[int(row[0]) - 1, int(row[1]) - 1] = float(row[col])
    
    # save the matrix as np matrix
    np.save(f"{player}_means.npy", matrix)

def eval_training_session():
    means = np.zeros((len(all_players), 10))
    stds = np.zeros_like(means)
    n_episodes = 20
    for i, model_path in enumerate(tqdm(all_players)):
        for j in range(1, 11):
            env = make_vec_env(EndlessRunnerEnv, n_episodes, env_kwargs={"difficulty": (j, 0)})
            mean, std = evaluate_policy(PPO.load(model_path), env, n_eval_episodes=n_episodes)
            means[i, j-1] = mean
            stds[i, j-1] = std
    np.save(f"{checkpoint_folder}_train_session", means)
    np.save(f"{checkpoint_folder}_train_session_std", stds)

def wipe_data(folder):
    # Wipe anything in checkpoint_folder not ending with .zip
    for f in os.listdir(folder):
        if not f.endswith(".zip"):
            os.remove(f"{checkpoint_folder}/{f}")

if __name__ == "__main__":
    from model_config import checkpoint_folder, players, model, all_players
    ## Selecting players
    # evaluate_training_session(checkpoint_folder, EndlessRunnerEnv)
    # plot_scores(f"{checkpoint_folder}_train_evals.csv")
    # data = prepare_data(f"{checkpoint_folder}_train_evals.csv")
    # print_contenders(data)

    # Preparing difficulty matrix
    # eval_all_models(checkpoint_folder)
    # set players to all models in folder
    for player in tqdm(all_players):
        create_difficulty_matrix(player)
        create_ndarray(player)
        # create_ndarray(f"{player}_diff_mat.csv", f"{player}_std.npy", True)
    
    
    # subplot_difficulty_matrix(players)
    # player = "models/05_05/PPO_22_17/_44800000_steps"
    # create_difficulty_matrix(f"{player}.zip")
    # score1 = evaluate_model(player, EndlessRunnerEnv, (3, 0), 5)
    # score = evaluate_model_jason(player, EndlessRunnerEnv, (2, 0), 1)
    # print("jason: ", score)
    # plot_difficulty_matrix(f"{player}_means.npy")
    # subplot_all(all_players, 10, 10)
    
    # Prior
    # contenders = ["_400000_steps", "_7200000_steps", "_500000_steps",
    #           "_100000_steps", "_2600000_steps", "_1000000_steps",
    #           "_6700000_steps", "_5000000_steps", "_9700000_steps"]
    # # evaluate_models([f"models/04_14/PPO_07_08/{c}.zip" for c in contenders], EndlessRunnerEnv)
    # players = ["_1200000_steps", "_7600000_steps", "_6200000_steps"]
    # competencies = ["Low", "Mid", "High"]
    # for player in tqdm(players):
    #     create_difficulty_matrix(f"models/04_14/PPO_07_08/{player}.zip")
        # plot_difficulty_matrix(f"models/04_14/PPO_07_08/{player}_diff_mat.csv")
    # eval_training_session()
# 1209 407
# 1222 266
# 1235 199
# 1236 254
# 1228 339
# 1231 375

# 24