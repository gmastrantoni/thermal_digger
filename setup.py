from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="thermal_analyzer",
    version="2.0.0 (beta)",
    author="Giandomenico Mastrantoni",
    author_email="giandomenico.mastrantoni@uniroma1.it",
    description="A tool for analyzing thermal image time series data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gmastrantoni/thermal_analyzer.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "thermal-analyzer=thermal_analyzer.main:main",
        ],
    },
)