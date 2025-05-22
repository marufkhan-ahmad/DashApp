from setuptools import setup, find_packages

setup(
    name="campaign_dashboard",
    version="0.1.0",
    description="A dashboard application to visualize campaign data from SQL Server",
    author="Maruf khan",
    author_email="mk7446683@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],  # Reference to main.py at project root
    install_requires=[
        "dash>=2.17.0",
        "pandas>=2.2.2",
        "plotly>=5.22.0",
        "pyodbc>=5.1.0",
    ],
    entry_points={
        "console_scripts": [
            "run-dashboard=main:main",
        ],
    },
    python_requires=">=3.10",
)
