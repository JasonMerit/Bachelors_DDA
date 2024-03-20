import torch as th
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, ProgressBarCallback
import wandb
from wandb.integration.sb3 import WandbCallback
# https://docs.wandb.ai/guides/integrations/stable-baselines-3

from ai.environment import EndlessRunnerEnv

def train(save_path: str, total_timesteps: int = 1e6):
    save_path = save_path

    policy_kwargs = dict(activation_fn=th.nn.ReLU, net_arch=[4, 4])
    checkpoint_callback = CheckpointCallback(
        save_freq=total_timesteps//10,
        save_path=save_path,
        name_prefix=""
        )

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

    # model = PPO(config["policy"], EndlessRunnerEnv(),
    #             policy_kwargs=policy_kwargs, seed=42)  # Seed for reproducibility
    # model.learn(total_timesteps=config["total_timesteps"], 
    #             callback=[wandb_callback, ProgressBarCallback()])

    model = PPO("MlpPolicy", EndlessRunnerEnv(),
                policy_kwargs=policy_kwargs, seed=42)  # Seed for reproducibility
    model.learn(total_timesteps=total_timesteps, 
                callback=[checkpoint_callback, ProgressBarCallback()])
    model.save(path=save_path)
    # run.finish()
        

def get_save_path():
    from datetime import datetime
    name = datetime.now().strftime("%m_%d/PPO_%H_%M")
    return f"models/{name}"
    
if __name__ == "__main__":
    train(get_save_path(), total_timesteps=1000)
    