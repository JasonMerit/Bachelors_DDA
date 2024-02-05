class Game:
    def __init__(self):
        self.data = []

    def create_new_data(self):
        # Your logic to create new data goes here
        new_data = "New Data"
        self.data.append(new_data)

class DisplayManager:
    def __init__(self):
        self.display_callbacks = []

    def attach_display_callback(self, callback):
        self.display_callbacks.append(callback)

    def update_display(self, data):
        for callback in self.display_callbacks:
            callback(data)

class Display:
    def __init__(self):
        pass  # No need to reference the Game class here

    def draw(self, data):
        # Your drawing logic goes here using data
        print("Updating visuals:", data)

def main():
    game = Game()
    display_manager = DisplayManager()
    display = Display()

    # Attach the display callback to the display manager
    display_manager.attach_display_callback(display.draw)

    for _ in range(5):
        # Simulate creating new data in the game
        game.create_new_data()

        # Update the display through the display manager
        display_manager.update_display(game.data)

if __name__ == "__main__":
    main()
