from stable_baselines3 import PPO

from ai.environment import EndlessRunnerEnv
from game.controls import Controller
from game.config import Config

class PlayModel():
    def __init__(self, model_path: str):
        Config.caption += f" - Model: [{model_path[7:-4]}]"
        self.env : EndlessRunnerEnv = EndlessRunnerEnv(render=True)
        self.model = PPO.load(model_path, env=self.env)

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
    
    def pause(self):
        self.paused = not self.paused
    
    def reset(self):
        self.game.reset()
 
    def play(self):
        state, _ = self.env.reset(42)  # Seed for reproducibility
        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()
            self.controller.handle_events()

            action, _ = self.model.predict(state)
            state, reward, terminal, truncated, _ = self.env.step(action)
            done = terminal or truncated
            if done:
                state, _ = self.env.reset()
            self.env.render(state)

def get_latest_model(date: str, model: str):
    if model:
        assert date, "Date is required when specifying model"
        return f"models/{date}/PPO_{model}.zip"

    import os
    folder = f"models/{date}" if date else "models"
    models = [os.path.join(root, dir) 
            for root, dirs, _ in os.walk(folder) 
            for dir in dirs if dir.startswith("PPO")]
    
    assert models, f"No models found. Bad date? {date}"
    return max(models, key=os.path.getctime) + ".zip"


if __name__ == "__main__":
    import argparse
    # optional argument of model path MM_DD
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", type=str, default="")
    parser.add_argument("-m", "--model", type=str, default="")
    args = parser.parse_args()

    path = get_latest_model(args.date, args.model)
    print("Playing model:", path)
    play_model = PlayModel(path)
    play_model.play()