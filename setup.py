import setuptools

with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SpotifyUtil",
    version="0.0.0.8",
    author="Arg0naut18",
    description="SpotifyUtils is a very useful library made over Spotipy to automate some rather tiring tasks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arg0naut18/SpotifyUtil",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords = [
        "Spotify",
        "Spotipy",
        "SpotifyUtil",
        "SpotifyUtils",
    ],
    python_requires=">= 3.8",
    include_package_data=True,
    install_requires=["spotipy"]
)