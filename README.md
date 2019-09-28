# Python Xplane

## Firewall config

In Windows Rechner in erweiterten Firewall Einstellungen die vorgefertigten Xplane Regeln gelöschtund eine iegene Hinugefügrt, die Incoming Traffic auf Port 49000 von jeden Rechner erlaubt.  

Beim Linux Rechner folgende iptables Regel hinzugefügt

``` shell
sudo iptables -I INPUT -p udp --dport 49000 -j ACCEPT
```
