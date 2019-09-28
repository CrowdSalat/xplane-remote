# Python Xplane

## Firewall config

In Windows Rechner in erweiterten Firewall Einstellungen die vorgefertigten Xplane Regeln gelöschtund eine iegene Hinugefügrt, die Incoming Traffic auf Port 49000 von jeden Rechner erlaubt.  

Beim Linux Rechner folgende iptables Regel hinzugefügt

``` shell
sudo iptables -I INPUT -p udp --dport 49000 -j ACCEPT
```

## XPlane Datenschnittstellen Dokumentation

Das Ziel an das Dataoutput kann über die GUI eingestellt werden. Alternativ auch Programmatisch über Sockets.

Für Dataref kann in der GUI Lesend und Schreibend aktiviert werden. Schreibend heißt, dass UDP Packete an das angebene Ziel gesendet  werden. Kann Alternativ Programmatisch geöffnet werden. Lesend scheint keine Auswirkung zu haben, die Schreibenden Python Skripte funktionieren dennoch.

Xplane unterscheidet zwischen Dataref und Dataoutputs. Beide Wege sind in Dokumenation unter C./xplane/ TODO gespeichert.

DataRef Lesen: 
S. 12 
'SEND ME ALL THE DATAREFS I WANT: RREF'

DataRef Schreiben:
S. 14
'SET A DATAREF TO A VALUE: DREF'

DataOutput schreiben:
S. 15
SET A DATA OUTPUT TO A VALUE: DATA

Seite 14 der Dokumentation beschreibt wie einzelne DataRefs beschrieben und gelesen werden können.
