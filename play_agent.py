from game.display import Display
from game.controls import Controller
from ai.environment import EndlessRunnerEnv
from ai.agent import Agent

class PlayAgent():
    def __init__(self):
        self.env = EndlessRunnerEnv(Display())

        self.key_actions = {
            "quit": self.quit,
            "pause": self.pause, 
            "reset": self.env.reset,
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
        
        agent = Agent()
        state = self.env.reset()
        while self.playing:
            # Pausing the game
            while self.paused:
                self.controller.handle_events()
            
            self.controller.handle_events()

            action = agent.get_action(state)
            # action = env.action_space.sample()
            state, reward, done, _ = self.env.step(action)

            if done:
                state = self.env.reset()
            self.env.render()


if __name__ == "__main__":
    play_agent = PlayAgent()
    play_agent.play()