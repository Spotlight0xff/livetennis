###Installation
* python3 is needed (use pip3 if pip is aliased as python2-pip)
* `apt-get install libxml2-dev libxslt1-dev python-dev`
* `git clone git@github.com:Spotlight0xff/livetennis.git`
* `cd livetennis`
* `sudo pip install -r requirement.txt`

###Usage
`./livetennis.py -h`

###Sample configuration file
```[Database]
; IP of mysql instance
Host=192.168.0.200

; Port of MySQL instance
Port=3306

; MySQL user
User=root

; Password for MySQL user
Password=abc123

; Database name to be used
Name=test_ptl

[Filter]
; tournament IDs (check ./livetennis.py -l)
Whitelist=0448,0656

; set to 1, if you want double matches as well
Doubles=0```
