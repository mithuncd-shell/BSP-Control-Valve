# ########## Module Information #############
# Module : GlobalVariables
# Purpose : To Save all configurations that the program uses throughout
# Authors :
# Shashi, Karthick Kumar (karthick.shashi@shell.com)
# Last Modified:04-Dec-2018

# Loading Libraries for Control valve Project

# PI server connectivity related library
from win32com.client.dynamic import Dispatch

# Machine Learning Libraries Start #
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
# Machine Learning Libraries End #

# Library for handling datetime data
from datetime import datetime as datetime
from datetime import timedelta
from dateutil import tz
import pandas as pd
import numpy as np

# importing basic libraries
import os
import sys
import json
import time
import pickle
import shutil
import glob
import dill

#import logging libraries
# To Do: Add
import logging
import os
from time import strftime

# Import library for email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
# Importing libraries end #


CWD = os.getcwd()
os.chdir(CWD)
os.chdir("C:/PAM/bsp_control_valve/Code/src")
master_file = r"..\data\training\master_data\master_data_v2.pkl"
model_path = r"..\data\training\models"
deployment_path = r"..\data\live\models"
config_path = r"..\data\training\configs"
log_path= r"..\data\logs"
try:
    LOG_FILENAME = log_path + "./" + str.upper(sys.argv[2]) + '_' + str.lower(sys.argv[1]) + '_'  + strftime("%m-%d-%Y_%H-%M.txt")
except:
    LOG_FILENAME='Log.txt'

FORMAT = '%(asctime)s -  %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format=FORMAT ,filemode='w')


