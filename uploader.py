import boto3
import ConfigParser
import argparse
import os
import zipfile
import glob

#Setting up arguments for script
parser = argparse.ArgumentParser(description='Easy to use function upload tool for Amazon Lambda')
parser.add_argument('--coffee', help='argument to change coffescript files to js files before upload', action='store_true')
parser.add_argument('--config', help='specify path to configuration file. Example: /root/functions.ini', required=True)
parser.add_argument('--function', help="function from config file to upload to lambda")
args = parser.parse_args()

#Read in Configuration File
Config = ConfigParser.ConfigParser()
Config.read(args.config)


#If Files are Coffee
if args.coffee == True:
  os.system("coffee --compile " + Config.get(args.function, "dirPath"))

#Change to directory of function and build Zip File
os.chdir(Config.get(args.function, "dirPath"))
zipFile = args.function+".zip"
zf = zipfile.ZipFile(zipFile, mode='w')
files = glob.glob("*.js")

for file in files:
  zf.write(file)

zf.close()

#Setup AWS Session to Lambda
session = boto3.Session(aws_access_key_id=Config.get("aws", "aws_access_key_id"),
                        aws_secret_access_key=Config.get("aws", "aws_secret_access_key"),
                        region_name=Config.get("aws", "region_name"))

client = session.client('lambda')

#Zipfile has to be sent as binary
fileUpload = open(zipFile)

#Upload Zip to Lambda
client.upload_function(FunctionName=Config.get(args.function, "Name"), FunctionZip=fileUpload, Runtime=Config.get(args.function, "Runtime"), Role=Config.get(args.function, "Role"), Handler=Config.get(args.function, "Handler"), Mode=Config.get(args.function, "Mode"))
