from setuptools import setup, find_packages

setup(
    name="cli-obsidian",
    version="1.0.0",
    description="CLI interface for Obsidian - Make your notes agent-native",
    author="CLI Skill Factory",
    author_email="cli-skill-factory@example.com",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "pyyaml>=6.0",
        "rich>=13.0",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-obsidian=cli_anything.obsidian.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="obsidian cli automation agent ai",
    include_package_data=True,
    package_data={
        "cli_anything.obsidian": ["skills/*.md"],
    },
)
