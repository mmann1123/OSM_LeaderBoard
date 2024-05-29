from setuptools import setup, find_packages

setup(
    name="OSM_LeaderBoard",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "dash",
        "pandas",
        "geopandas",
        "requests",
        "pyyaml",
        "datetime",
        "dash_uploader",
        "dash_table",
        "shapely",
        "folium",
        "matplotlib",
        "mapclassify",
        "flask",
    ],
    entry_points={
        "console_scripts": [
            "leaderboard=osm_leaderboard.dash_app:main",
        ],
    },
    author="Michael Mann",
    author_email="mmann1123@gmail.com",
    description="An application to analyze and display OSM leaderboards.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/OSM_LeaderBoard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
