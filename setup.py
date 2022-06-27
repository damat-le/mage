from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mage',
    version='0.1.0',
    keywords='reinforcement learning, environment, gridworld, agent, rl, openaigym, openai-gym, gym, multi-agent',
    url='https://github.com/damat-le/mage',
    description='Multi-Agent Grid Environment',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['mage'],
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    python_requires=">=3.7",
    author="Leo D'Amato",
    author_email="leo.damato.dev@gmail.com",
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"]
)
