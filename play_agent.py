from game.display import Display
from game.controls import Controller
from game.entities import Player, Platform
from ai.environment import EndlessRunnerEnv
from ai.agent import CheaterAgent

class PlayAgent():
    def __init__(self):
        self.env = EndlessRunnerEnv(render=True)

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
        
        agent = CheaterAgent()
        state, _ = self.env.reset()
        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()
            
            self.controller.handle_events()

            action = agent.predict(state)
            # action = env.action_space.sample()
            state, reward, terminal, truncated, _ = self.env.step(action)
            done = terminal or truncated
            if done:
                # self.env.render()
                # self.pause()
                # while self.paused:
                #     self.controller.handle_events()
                state, _ = self.env.reset()
            self.env.render()


if __name__ == "__main__":
    play_agent = PlayAgent()
    play_agent.play()