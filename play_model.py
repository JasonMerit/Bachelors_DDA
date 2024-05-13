import numpy as np
from stable_baselines3 import PPO
from icecream import ic

from reinforcement_learning.environment import EndlessRunnerEnv, TileER, Parrot
from game.controls import Controller
from game.config import Config

class PlayModel():
    def __init__(self, model_path: str, Env, difficulty=(5,0)):
        Config.caption += f" - Model: [{model_path[7:-4]}]"
        Config.FPS = 100
        self.env: EndlessRunnerEnv = Env(difficulty=difficulty, render=True, truncated=False)
        # self.env: EndlessRunnerEnv = Env(render=True, truncated=False)
        self.model: PPO = PPO.load(model_path, env=self.env)

        self.key_actions = {
            "quit": self.quit,
            "pause": self.pause, 
            "reset": self.env.reset,
            "increase_speed": Controller.increase_speed,
            "decrease_speed": Controller.decrease_speed,
            "increase_difficulty": self.increase_difficulty,
            "decrease_difficulty": self.decrease_difficulty,
            "render": self.toggle_render
        }

        self.controller = Controller(self.key_actions)
        
        self.playing = True
        self.paused = False
        self.render = True
    
    def quit(self):
        self.playing = False
        quit()
    
    def pause(self):
        self.paused = not self.paused
    
    def reset(self):
        self.env.reset()
    
    def toggle_render(self):
        self.env._render = not self.env._render

    def increase_difficulty(self):
        new_diff = (self.env.game.difficulty[0] + 1) % 11
        self.env.game.set_difficulty((new_diff, self.env.game.difficulty[1]))

    def decrease_difficulty(self):
        new_diff = (self.env.game.difficulty[0] - 1)
        if new_diff < 0:
            new_diff = 10
        self.env.game.set_difficulty((new_diff, self.env.game.difficulty[1]))
 
    def play(self):
        model = self.model
        env = self.env
        n_episodes = 100
        
        obs, _ = env.reset()
        rewards = np.zeros(n_episodes)
        done = False
        # deaths = []
        for episode in range(n_episodes):
            total_reward = 0.0
            while not done:
                self.controller.handle_events()
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, term, trunc, _ = env.step(action)
                ic(obs)
                total_reward += reward
                done = term or trunc
            rewards[episode] = total_reward
            
            # store the history of the game
            # deaths.append(env.game.history.copy())
            obs, _ = env.reset()
            done = False
        # 
        # save deaths to a file
        # import pickle
        # with open('deaths.pkl', 'wb') as f:
        #     pickle.dump(deaths, f)

        print(f"R({np.mean(rewards):.2f}, {np.std(rewards):.2f})")
        print(rewards)

        # R(86.00, 142.63)



if __name__ == "__main__":
    Env = EndlessRunnerEnv
    from model_config import checkpoint_folder, players, model
    with open("logs.csv", "r") as f:
        lines = f.readlines()
        last = lines[-1].split(", ")
        path = last[0] + ".zip"
    
    model = "_100000_steps"
    path = f"{checkpoint_folder}/{model}"
    # path = "models/05_05/PPO_22_17/_90600000_steps.zip"
    path = "models/05_05/PPO_22_17/_44100000_steps.zip"
    path = "models/05_08/PPO_12_50.zip"
    path = "models/05_12/PPO_14_26/_10000000_steps.zip"  # PERCFECT
    path = "models/05_13/PPO_21_25/_100000_steps.zip"
    print(f"Playing [{path}] in [{Env.__name__}]")

    play_model = PlayModel(path, Env, (6, 0))
    play_model.play()
    