"""
Setup configuration for TestRig Automator.
Install with: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="TestRig-Automator",
    version="2.3.0",
    description="Professional WLAN testbed automation tool with modular architecture",
    author="Test Engineering",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.31.0",
        "pandas>=2.0.0",
        "paramiko>=3.0.0",
        "pyserial>=3.5",
    ],
    entry_points={
        "console_scripts": [
            "testrig-automator=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
