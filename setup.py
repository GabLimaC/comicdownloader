from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
  requirements = f.read().splitlines()
print(requirements)
setup(
  name="comic_translator",
  version="0.1.0",
  packages=find_packages(where="src"),
  package_dir={"": "src"},
  python_requires=">=3.10,<3.12",
  install_requires=requirements,  # Add this line
)