from gym.envs.registration import register

register(
    id='SimpleMultiGrid-v0',
    entry_point='gym_smg:SMGEnv',
    max_episode_steps=200
)

register(
    id='SimpleMultiGrid-8x8-v0',
    entry_point='gym_smg:SMGEnv',
    max_episode_steps=200,
    kwargs={'map_name': '8x8'},
)

register(
    id='SimpleMultiGrid-4x4-v0',
    entry_point='gym_smg:SMGEnv',
    max_episode_steps=200,
    kwargs={'map_name': '4x4'},
)