import argparse
import Bachelors_DDA.Game.config as config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the endless runner game")
    parser.add_argument("--render", action="store_true", help="Render the game")
    parser.add_argument("--agent", action="store_true", help="Run the agent")
    # parser.add_argument("--god", action="store_true", default=False, help="Run with god mode")
    # god mode that defaults to false
    parser.add_argument("--god", action="store_true", help="Run with god mode")
    args = parser.parse_args()

    config.GOD_MODE = args.god
    print(args.god)
    if args.render:
        if args.agent:
            from environment import main
        else:
            from Bachelors_DDA.Game.display import main
    else:
        from Bachelors_DDA.Game.endless_runner import main
    main()