"""
Simple Web Search Skill - Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="simple-websearch-skill",
    version="1.0.0",
    author="Yaya",
    description="Simple Web Search - 极简网络搜索技能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="web search baidu bing internet",
)
