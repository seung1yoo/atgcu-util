from setuptools import setup, find_packages

setup(
    name="ica-data-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "biopython>=1.80",      # For biological sequence handling
        "icav2",                # ICA v2 CLI
        "tabulate>=0.9.0",      # For table formatting
        "click>=8.0.0",         # For CLI interface
    ],
    entry_points={
        'console_scripts': [
            'ica-manager=ica_data_manager.cli:cli',
        ],
    },
    author="ATGCU",
    author_email="your.email@example.com",
    description="ICA (Illumina Connected Analytics) Data Management Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seung1yoo/atgcu-util/ica-data-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
) 