# MakevCard

  MakevCard is a beeware briefcase python app which is used to convert a table(having \*phone number and name) to vCard and make it easier to import it to device contacts

 ## In Process

  Made a test using tablib which is successfull 
	[x] tablib code - initial test

  ### Balance work:
  	
  	[ ] Writing .vcf logic
  	[ ] Combining tablib to .vcf to main.py
  	[ ] Testing main.py
  	[ ] Making front-end using beeware togo
  	[ ] Connecting them all
  	[ ] Distributing... as desktop app[linux,win,mac]
  	[ ] Workaround for android
  	[ ] Make this app upgradable

 ## Usage:
 
 ### Create venv
 ``` bash
python -m venv venv #you can also use other methods
 ```
 	For bash
 ```bash
 source venv/bin/avtivate
 ```
 	For cmd
 ``` cmd
./venv/Scripts/activate
 ```

 ### Run test.py (soon changes to main.py) [refer here](#balance-work)
 
 ``` bash
cd test
python test_read.py # as this is the main code and test_write.py is for generating those table files in python to read that in test_read
 ```