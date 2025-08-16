"""Setup configuration for local-agent package"""

from setuptools import setup, find_packages

with open("requirements-minimal.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("requirements-dev.txt") as f:
    dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="local-agent",
    version="0.1.0",
    description="Multi-agent system for autonomous code analysis and generation",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "all": open("requirements.txt").read().splitlines()
    },
    entry_points={
        "console_scripts": [
            "local-agent=agent_system:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)