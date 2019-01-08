from setuptools import setup

setup(
    name='mycroft_engines',
    version='0.1',
    packages=['mycroft_intent_engines', 'mycroft_intent_engines.skills',
              'mycroft_intent_engines.engines'],
    url='https://github.com/JarbasAl/mycroft_intent_engines',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='utils to add intent engines for mycroft'
)
