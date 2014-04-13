import os

SQLALCHEMY_DATABASE_URI = 'postgres://sxmcazelqcfszj:8mV7XaN_wEgna8uuYTBQH5PyY5@ec2-54-204-2-217.compute-1.amazonaws.com:5432/d3d3ka1rcf20ed'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
