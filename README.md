Installation
---

* python3 is needed (use pip3 if pip is aliased as python2-pip)
* `apt-get install libxml2-dev libxslt1-dev python-dev`
* `git clone git@github.com:Spotlight0xff/livetennis.git`
* `cd livetennis`
* `sudo pip install -r requirement.txt`

Usage
---
`./livetennis.py -h`

Sample configuration file
---
```ini
[Database]
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
Doubles=0
```


Database configuration
---

```sql
CREATE TABLE `matches` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `year` year(4) NOT NULL,
  `tournament_id` varchar(20) NOT NULL,
  `match_id` varchar(20) NOT NULL,
  `table_name` varchar(255) NOT NULL,
  `t_name` varchar(50) NOT NULL,
  `t_category` varchar(5) NOT NULL,
  `status` varchar(10) NOT NULL,
  `is_doubles` int(11) NOT NULL,
  `is_quals` tinyint(1) NOT NULL,
  `num_sets` int(11) NOT NULL,
  `id1` varchar(10) NOT NULL,
  `id2` varchar(10) NOT NULL,
  `player1` varchar(255) NOT NULL,
  `player2` varchar(255) NOT NULL,
  `round` varchar(10) NOT NULL,
  `winner` varchar(20) NOT NULL,
  `score` varchar(20) NOT NULL,
  `first_server` varchar(55) NOT NULL,
  `start_ts` varchar(20) NOT NULL,
  `matchtime` varchar(20) NOT NULL,
  `retirement` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```
