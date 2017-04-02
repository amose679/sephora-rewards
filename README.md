# sephora-rewards

A little script that will hit the sephora rewards page and send a text for any new, limited edition rewards.

I've included a sample config file, you you can get your own twilio account and credentials at https://www.twilio.com/.

I used postgres to save the rewards I'd already alerted on, and have it running on a cron
job with run_script.sh 

To run the python:
pip install requirements.txt
python main.py

I've included the bash file I use to run the script on a crontab, modify it to work with your
own virtualenv set up