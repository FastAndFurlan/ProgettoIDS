Referinfo
Osservatorio referendum progetto d'esame per Informatica diritto e società, aggrega dati storici di referendum in un unico strumento consultabile con filtri.
COME SI AVVIA IL PROGETTO
Istruzioni per chi riceve intera cartella:
1 verificare che python sia installato.

2 dopo aver scompattato la cartella principale ed essere entrati copiare il percorso e raggiungerlo da terminale con cmd.

3installare flask (pip install flask pandas) se pip non riconosciuto provare python -m pip install flask pandas

4 una volta completate le installazioni sempre dal terminale lanciare App.py (python App.py).

5 se tutto è andato per il meglio il messaggio dovrebbe contenere un indirizzo simile o uguale a http://127.0.0.1:5000, basterà copiarlo/incollarlo nel proprio browser per avere il progetto disponibile da visualizzare

6 per chart.js serve connessione a internet altrimenti è impossibile vedere i grafici dei dati richiesti

EVENTUALI PROBLEMI NELL'AVVIO DEL PROGETTO
- ModuleNotFoundError: alcune librerie non sono state installate correttamente, vedere punto 3.

- Impossibile raggiungere il sito in risposta browser: il server non è in esecuzione (controllare il terminale e di aver avviato App.py) oppure sta venendo utilizzato un indirizzo differente da quello specificato nel risultato della stessa App.py

- Pagina si apre ma menu a tendina/stile vuoti: il file forse è stato aperto come file locale (doppio click su index.html o tramite LiveServer di VSCode), le istruzioni non sono state seguite, ricontrollare punto 4.

- FileNotFoundError: riferito di solito al file CSV impiegato, il terminale potrebbe non essere aperto nella cartella corretta, verifica punto 2.

