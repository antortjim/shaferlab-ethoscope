"""
my docstring

"""
from distutils.core import setup

setup(
    name='ethoscope',
    version='trunk',
    author=['Quentin Geissmann', 'Giorgio Gilestro', 'Luis Garcia'],
    author_email= ['quentin.geissmann13@imperial.ac.uk','g.gilestro@imperial.ac.uk', 'luis.garcia@polygonaltree.co.uk'],
    packages=['ethoscope',
               'ethoscope.tracking',
               'ethoscope.utils',
               'ethoscope.web_utils',
               'ethoscope.hardware_control',
              ],
    url="https://github.com/gilestrolab/ethoscope",
    license="GPL3",
    description='todo', #TODO
    long_description=open('README').read(),
    scripts=['scripts/sleep_monitor_pi_automask.py', 'scripts/record_video.py'],
    # data e.g. classifiers can be added as part of the package
    # TODO
    # package_data={'ethoscope': ['data/classifiers/*.pkl']},
    # extras_require={
    #     'pipes': ['picamera>=1.8'],
    # },
    install_requires=[
        "numpy>=1.6.1",
        "pyserial>=2.7",
        "bottle>=0.12.8",
        "MySQL-python >= 1.2.5",
        "cherrypy >= 3.6.0",
        "scipy >= 0.15.1"
    ],
)
