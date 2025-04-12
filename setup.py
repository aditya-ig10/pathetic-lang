from setuptools import setup, find_packages

setup(
    name="pathetic",                     # Package name
    version="0.1",                       # Version
    packages=find_packages(),            # Automatically find all subfolders with __init__.py
    entry_points={
        "console_scripts": [
            "pathetic=pathetic.cli:main",  # Run `pathetic` → calls main() in pathetic/cli.py
        ],
    },
)
