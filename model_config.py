import os
checkpoint_folder = "models/05_13/PPO_21_29"
players = ["500000", "7000000", "5800000"]
model = 100000

# checkpoint_folder = "models/04_18/PPO_12_23"
# players = ["_1200000_steps", "_7000000_steps", "_5800000_steps"]
# checkpoint_folder = "models/04_19/PPO_12_46"
# players = ["300000", "7100000", "3500000"]

players = [f"{checkpoint_folder}/_{p}_steps" for p in players]
model = f"_{model}_steps.zip"
abilities = ["Low", "Mid", "High"]

all_players = [checkpoint_folder + "/" + f[:-4] for f in os.listdir(checkpoint_folder) if f.endswith(".zip")]
all_players.sort(key=lambda x: int(x.split("_")[-2]))
