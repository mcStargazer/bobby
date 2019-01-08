# bobby
This repo contains materials for a talk, "I Spy with MySQLi", given at the OKCPython Meetup on Jan 09, 2019.
Details on the venue can be found at https://www.meetup.com/okcpython/events/vtdhfpyzcbmb/. The purpose is to raise awareness of security issues so every webapp can run more safely and do it's intended job.

To run "the_app.py" you'll need a software environment similar to mine. The Python environment I used is detailed in the "environment.yml" (exported with conda). My mysql server details are: Ver 14.14 Distrib 5.7.24, for Linux (x86_64), and it's running on Ubuntu 18.04 LTS.

You'll need to create a mysql user that has SELECT, INSERT, UPDATE, CREATE, and DROP grants on the database you will use. Also, make sure to change the path inside "the_app.py" so that your script can find your "db_creds.json" file. This json file should have the correct credentials for the mysql user you created for this app.

Any omissions here? Likely. Message me if I've left any important code or configuration settings out. I'll help if I can.

Legal Notice: Penetration testing should only be conducted within an isolated testing environment that you own, or for a client with whom clear rules of engagement have been agreed upon and contracted. Let's keep our hacking ethical!
