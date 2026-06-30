### The UnicodeDecodeError: 'utf-8' codec can't decode byte 0x... in position ...: invalid continuation byte (or similar messages like invalid start byte)

Solved by removing the "%  sign from the password. 


###  Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:11434 -> 127.0.0.1:0: listen tcp 0.0.0.0:11434: bind: Normalt tillåts bara en användare för varje socketadress (protokoll/nätverkadress/port).


Occurs when another process is already using the port in question. 
Run "netstat -bno" to investigate which process that is connected to the port.
If desired result show up. Then further research is required. 
In this case, ollama uses port 11434. 

In this case, the ollama native install caused conflict with the ollama in the docker container. 
Both listened to the port. Solved but turning off wifi access for the ollama native install.

### Getting this when putting localhost UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf6 in position 71: invalid start byte

This was a very strange error and I can't quite figure out how to reproduce it. 
I noticed two problems when troubleshooting:
1. We ran postgres natively on windows and the docker container(both on the same port)
2. The errors came back in Swedish, which could have been connected with the encoding problems(erros and variables)

I added this in the docker yaml:
LANG: en_US.utf8
LC_ALL: en_US.utf8
POSTGRES_INITDB_ARGS: "--locale=en_US.UTF-8"

### Multiple connection attempts failed. All failures were:
- host: 'localhost', port: 5432, hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: FATALT:  L�senordsautentisering misslyckades f�r anv�ndare "userhere"
- host: 'localhost', port: 5432, hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: FATALT:  L�senordsautentisering misslyckades f�r anv�ndare "username3"
   Type: OperationalError

This is a tricky error, because whats reported is not exactly what happened. The problem here is that we are running
postgres on the windows computer and docker on the same port. This causes some type of collision. The clue in the 
error message is "**Multiple** connection attempts failed". Head into "Services" on windows and shutdown postgres. 


### psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: FATAL:  no pg_hba.conf entry for host "ip", user "postgres", database "events_db", no encryption

Multiple connection attempts failed. All failures were:
- host: 'localhost', port: 5432, hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: FATAL:  no pg_hba.conf entry for host "172.18.0.1", user "postgres", database "events_db", no encryption
- host: 'localhost', port: 5432, hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: FATAL:  no pg_hba.conf entry for host "ip", user "postgres", database "events_db", no encryption

Head into pgdata/pg_hba.conf and add the entry for the missing IP and subnet mask. 


### ollama._types.ResponseError: model 'llama3.2' not found (status code: 404)

run "ollama pull llama3.2". 

