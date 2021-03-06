import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='lowhaio_retry',
    version='0.0.5',
    author='Michal Charemza',
    author_email='michal@charemza.name',
    description='Wrapper that retries failed lowhaio HTTP requests',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michalc/lowhaio-retry',
    py_modules=[
        'lowhaio_retry',
    ],
    python_requires='>=3.6.3',
    test_suite='test',
    tests_require=[
        'lowhaio~=0.0.61',
        'aiohttp~=3.5.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
)
