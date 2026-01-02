# setup.py
from setuptools import setup

setup(
    name="gemini-cli",
    version="0.1",
    py_modules=["gemini"],
    install_requires=["google-genai"],
    entry_points={
        "console_scripts": [
            "gemini=gemini:main",
        ],
    },
)