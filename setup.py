from setuptools import setup, find_packages

setup(
    name='epydemics',
    version='0.5.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'seaborn',
        'python-box',
        'scikit-learn',
        'statsmodels',
    ],
    author='Juliho David Castillo Colmenares',
    author_email='juliho.colmenares@gmail.com',
    description='A module for modeling and analyzing epidemic data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # If using a markdown README file
    url='https://github.com/julihocc/epydemics',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Choose the appropriate license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify a minimum Python version
)
