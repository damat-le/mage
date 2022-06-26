from tabulate import tabulate

def log_iteration(history, obs, actions, dones):
    for idx, agent_pos_xy in enumerate(obs):
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

if __name__=='__main__':
    import logging, os, sys
    from gym_smg.env import SMGEnv
    from datetime import datetime as dt
    import random

    # Folder name for the simulation
    FOLDER_NAME = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    os.makedirs(f"log/{FOLDER_NAME}/")

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
    env = SMGEnv(
        num_agents=3,
        starts_xy=[(0, 0), (0, 7), (1,3)],
        goals_xy=[(4, 0), (4, 7), (1,7)],
        agents_colors=['yellow', 'blue', 'green'],
        disappear_on_goal=True,
        map_name="8x8"
        )
    obs, dones, _ = env.reset()


    logger.info("Running action-perception loop...")
    history = {f"A{i}":[] for i in range(env.n_agents)}

    for t in range(1200):
        env.render()

        actions = [random.choice(range(5)) for _ in range(env.n_agents)]
        log_iteration(history, obs, actions, dones)

        if all(dones):
            logger.info(f"...all agents are done at time step {t}")
            break

        obs, dones, _ = env.step(actions)

    log_history(history)
    env.close()
    logger.info("-------------END-------------")