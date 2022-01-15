#!/usr/bin/env bash
# stop script on error
set -e


echo "Davis Gateway starting .... wait for all services to start"
# Sleep for 5 miniutes before starting to give everything a chance to come up
sleep 300
echo "Davis Gateway now booting up."


cd /home/pi/prod/davisgw-aws

# Check to see if root CA file exists, download if not
 
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
fi

# Check to see if AWS Device SDK for Python is already installed, install if not
if ! python -c "import AWSIoTPythonSDK" &> /dev/null; then
  printf "\nInstalling AWS SDK...\n"
  pushd aws-iot-device-sdk-python
  pip install AWSIoTPythonSDK
  result=$?
  popd
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install SDK.\n"
    exit $result
  fi
fi

# run pub/sub sample app using certificates downloaded in package
printf "\nStarting gateway application...\n"
while true 
do
python /home/pi/prod/davisgw-aws/davis-gw.py -e a2dz4cozrsbfh4-ats.iot.us-east-1.amazonaws.com -r root-CA.crt -c mjrgw1.cert.pem -k mjrgw1.private.key
sleep 30
echo "Restarting gateway application."
done
