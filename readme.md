**Popa Claudia**: Interfață grafică în PyQt5 care implementează metoda bisecției pentru determinarea rădăcinilor unei funcții pe un interval dat.

**Funcționalități**:
* utilizatorul poate introduce o funcție manual sau o poate încărca dintr-un fișier text
* poate alege intervalul [a, b] pe care se face aproximarea
* poate specifica opțional numărul maxim de iterații
* poate alege tipul de precizie:
                             * pe bază de toleranță (epsilon)
                             * pe bază de număr de zecimale garantate
* poate selecta tipul de eroare:
                             * absolută
                             * relativă
                             * ambele
* se generează un grafic al erorii care arată evoluția acesteia pe parcursul iterațiilor (poate fi salvat)
* se generează un grafic al funcției pe intervalul ales (poate fi salvat)
* se realizează o animație a trasării funcției
           * animația pornește cu butonul START
           * poate fi oprită cu STOP
           * poate fi salvată sub formă de GIF
* ca output text se afișează:
  * soluția obținută prin metoda bisecției
  * numărul de iterații efectuate
  * dacă precizia cerută a fost atinsă sau nu
  * numărul de zecimale garantate (dacă este cazul)
  * o aproximație a rădăcinii exacte
  * eroarea față de aceasta

**Verificări**: Sunt implementate verificări precum: funcția trebuie introdusă într-un format acceptat de SymPy, nu sunt acceptate câmpuri goale, dacă a>b intervalul este corectat automat și utilizatorul este notificat, este obligatorie alegerea unui tip de precizie și a unui tip de eroare, câmpul pentru număr de iterații acceptă doar valori numerice, toleranța trebuie introdusă în formă științifică (ex: 1e-3), iar metoda nu este aplicată dacă f(a)\*f(b) ≥ 0

**Zisu Mircea**: Interfață grafică în PyQt5 care implementează metoda coardei pentru determinarea rădăcinilor unei funcții pe un interval dat.

**Funcționalități**:
* utilizatorul poate introduce o funcție manual sau o poate încărca dintr-un fișier text
* poate alege intervalul [a, b] pe care se face aproximarea
* poate specifica opțional numărul maxim de iterații
* poate alege tipul de precizie:
                             * pe bază de toleranță (epsilon)
                             * pe bază de număr de zecimale garantate
* poate selecta tipul de eroare:
                             * absolută
                             * relativă
                             * ambele
* se generează un grafic al erorii care arată evoluția acesteia pe parcursul iterațiilor (poate fi salvat)
* se generează un grafic al funcției pe intervalul ales (poate fi salvat)
* se realizează o animație a trasării funcției
           * animația pornește cu butonul START
           * poate fi oprită cu STOP
           * poate fi salvată sub formă de GIF
* ca output text se afișează:
  * soluția obținută prin metoda coardei
  * numărul de iterații efectuate
  * dacă precizia cerută a fost atinsă sau nu
  * numărul de zecimale garantate (dacă este cazul)
  * o aproximație a rădăcinii exacte
  * eroarea față de aceasta