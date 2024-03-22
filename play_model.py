import numpy as np
from stable_baselines3 import PPO

from reinforcement_learning.environment import EndlessRunnerEnv, DumbEnv
from game.controls import Controller
from game.config import Config

class PlayModel():
    def __init__(self, model_path: str, Env):
        Config.caption += f" - Model: [{model_path[7:-4]}]"
        self.env: EndlessRunnerEnv = Env(render=True, truncated=False)
        self.model: PPO = PPO.load(model_path, env=self.env)

        self.key_actions = {
            "quit": self.quit,
            "pause": self.pause, 
            "reset": self.env.reset,
            "increase_speed": Controller.increase_speed,
            "decrease_speed": Controller.decrease_speed
        }

        self.controller = Controller(self.key_actions)
        
        self.playing = True
        self.paused = False
    
    def quit(self):
        self.playing = False
        quit()
    
    def pause(self):
        self.paused = not self.paused
    
    def reset(self):
        self.env.reset()
 
    def play(self):
        model = self.model
        env = self.env
        n_episodes = 10
        obs, _ = env.reset()
        rewards = np.zeros(n_episodes)
        done = False
        for episode in range(n_episodes):
            while not done:
                self.controller.handle_events()
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, term, trunc, _ = env.step(action)
                rewards[episode] += reward
                done = term or trunc
                env.render()
            obs, _ = env.reset()
            done = False

        # while self.playing:
        #     # Pausing the game
        #     while self.paused:
        #         self.controller.handle_events()
        #     self.controller.handle_events()

        #     action, _ = model.predict(obs, deterministic=True)
        #     # action = env.action_space.sample()
        #     obs, reward, terminal, truncated, _ = env.step(action)
        #     done = terminal or truncated
        #     if done:
        #         obs, _ = env.reset()
        #     env.render(obs)
        print(f"R({np.mean(rewards):.2f}, {np.std(rewards):.2f})")
        print(rewards)

        # R(86.00, 142.63)



if __name__ == "__main__":
    Env = EndlessRunnerEnv
    # import tkinter as tk
    # from tkinter.filedialog import askopenfilename
    # tk.Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    # path = askopenfilename() # show an "Open" dialog box and return the path to the selected file

    # read latest model from logs.csv
    with open("logs.csv", "r") as f:
        lines = f.readlines()
        last = lines[-1].split(", ")
        path = last[0]
    print(f"Playing [{path}] in [{Env.__name__}]")
    play_model = PlayModel(path + ".zip", Env)
    play_model.play()