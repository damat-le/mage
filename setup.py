from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gym_smg',
    version='0.1.0',
    keywords='reinforcement learning, environment, gridworld, agent, rl, openaigym, openai-gym, gym, multi-agent',
    url='https://github.com/damat-le/gym-smg',
    description='Simple Multi-Agent Gridworld Environment',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['gym_smg'],
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    python_requires=">=3.7",
    author="Leo D'Amato",
    author_email="leo.damato.dev@gmail.com",
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"]
)
