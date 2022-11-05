#!/usr/bin/env bash
# stop script on error
set -e


echo "Davis Gateway starting .... wait for all services to start"
# Sleep for 5 miniutes before starting to give everything a chance to come up
sleep 3
echo "Davis Gateway now booting up."


cd /home/mrothera/prod/davisgw-aws

# Check to see if root CA file exists, download if not
 
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# run pub/sub sample app using certificates downloaded in package
printf "\nStarting gateway application...\n"
while true 
do
# Note:  Set the topic to verify to run in test mode to publish to the verify topic
python /home/mrothera/prod/davisgw-aws/davis-gw-aws-v2.py --client_id mjrgw1 --topic "$aws/things/mjrgw1/shadow/update" --endpoint a2dz4cozrsbfh4-ats.iot.us-east-1.amazonaws.com --ca_file root-CA.crt --cert mjrgw1-certificate.pem.crt --key mjrgw1-private.pem.key
echo "Restart detected.  Sleep."
sleep 30
echo "Restarting gateway application."
done
