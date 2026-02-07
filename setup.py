from setuptools import setup, find_packages

setup(
    name="hacksentinel",
    version="1.0.0",
    description="MindCore · Sentinel - Deterministic bug discovery tool",
    author="MindCore",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mindcore-sentinel=sentinel.cli:main",
        ],
    },
    python_requires=">=3.8",
)
