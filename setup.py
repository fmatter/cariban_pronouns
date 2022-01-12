from setuptools import setup


setup(
    name='cldfbench_cariban_pronouns',
    py_modules=['cldfbench_cariban_pronouns'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'cariban_pronouns=cldfbench_cariban_pronouns:Dataset',
        ]
    },
    install_requires=[
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
