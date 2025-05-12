'''
setup.py is an essential part of packaging and distributing python projects .It is used by setuptools 
(or distutils in older versions of python) to define configuration of your projects, such as metadata , 
dependencies and more
'''
## the find package treats the parent folder as a package where there is a __init__.py file 
from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    """
    this function will return list of requirements
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            # read lines from the file 
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                ## ignore the empty lines and -e.
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirement.txt file not found ")

    return requirement_lst


setup(
    name="Network Security",
    version="0.0.1",
    author="Mukund Dixit",
    author_email="mukunddixit5914@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)