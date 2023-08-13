import imageio
from tabulate import tabulate

# To run this example, you need tabulate or imageio.
# You can install them with pip:
# `pip install tabulate imageio`

def log_iteration(history, obs, actions, dones):
    for idx, agent_pos_xy in obs.items():
        history[f'A{idx}'].append((agent_pos_xy, actions[idx], dones[idx]))
    return None

def log_history(history):
    """
    Save the history of the simulation as a table in which each row is 
    an iterarion.
    """
    t = tabulate(
        history, 
        headers='keys', 
        tablefmt='presto', 
        showindex=True
    )
    with open(f'log/{FOLDER_NAME}/actionPerceptionLoop.txt', 'w') as f:
        f.write(t)
    return None

def log_img(t, frame):
    imageio.imwrite(f'log/{FOLDER_NAME}/img/{t}.png', frame)

def create_gif(frames):
    imageio.mimsave(f'log/{FOLDER_NAME}/movie.gif', frames)

if __name__=='__main__':
    import logging, os, sys
    from mage.env import MAGE
    from datetime import datetime as dt
    import random

    # Folder name for the simulation
    FOLDER_NAME = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    os.makedirs(f"log/{FOLDER_NAME}/img")

    # Logger to have feedback on the console and on a file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"log/{FOLDER_NAME}/log.txt"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    logger.info("-------------START-------------")
    # Instantiate environment from problem instance
    env = MAGE(
        num_agents=3,
        starts_xy={0:(0, 0), 1:(0, 5), 2:(1,3)},
        goals_xy={0:(4, 0), 1:(4, 7), 2:(1,7)},
        agents_colors={0:'yellow', 1:'blue', 2:'green'},
        disappear_on_goal=True,
        obstacle_map="8x8"
        )
    obs, dones, _ = env.reset()

    logger.info("Running action-perception loop...")
    history = {f"A{i}":[] for i in range(env.n_agents)}

    frames = []

    for t in range(500):
        img = env.render(caption=f"t:{t}")
        log_img(t, img)
        frames.append(img)

        actions = {idx:random.choice(range(5)) for idx in range(env.n_agents)}
        log_iteration(history, obs, actions, dones)

        if all(dones):
            logger.info(f"...all agents are done at time step {t}")
            break

        obs, dones, _ = env.step(actions)

    log_history(history)
    env.close()
    create_gif(frames)
    logger.info("...done")
    logger.info("-------------END-------------")