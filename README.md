# Python Xplane

## Firewall config
** Beachte Updates. Deepin Update hat regeln gelöscht, danach lief kein lesender Zugriff mehr, da die Ports blockierten **

In Windows Rechner in erweiterten Firewall Einstellungen die vorgefertigten Xplane Regeln gelöschtund eine iegene Hinugefügrt, die Incoming Traffic auf Port 49000 von jeden Rechner erlaubt.
Die anderen Port eigentlich nicht geöffnet, klappt dennoch..

Beim Linux Rechner alle eingehenden UDP Ports geöffnet, da in der Bibliothek pyxpudpserver mehrere Sockets auf verschiedenen Ports geöffnet werden.

``` shell
sudo iptables -I INPUT -p udp -j ACCEPT
```

## Bibliotheken
https://github.com/leleopard/pyXPUDPServer
```
pip3 install pyxpudpserver
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
