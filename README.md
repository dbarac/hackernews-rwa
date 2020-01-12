# hackernews clone projekt za RWA

## Opis

Korisnici objavljuju linkove za koje drugi korisnici glasaju. Na početnoj stranici objave mogu biti rangirane po starosti, top, ili rising. Korisnici mogu komentirati objave, odgovarati na komentare, uređivati svoje komentare i glasati za druge komentare. Za svakog korisnika se mogu dohvatiti njegove objave i komentari.

## Instalacija i pokretanje aplikacije

1. klonirati git repo
   
   > git clone https://github.com/dbarac/hackernews-rwa.git

2. baza

   Instalirati i pokrenuti MySQL 8.

   Pokrenuti SQL skriptu za stvaranje usera i definiranje baze.

   >$ mysql -p < hackernews_rwa/schema.sql

3. Python okruženje i instalacija potrebnih paketa
   
   Aplikacija je testirana sa Python verzijom 3.7

   Nakon instalacije Python-a instalirati pakete i aplikaciju

   >$ pip install -r requirements.txt
   >$ pip install -e .

4. Postavljanje environment varijabli i pokretanje aplikacije

   >$ export FLASK_APP=hackernews_rwa
   >$ export FLASK_ENV=development
   >$ flask run

   Frontend će biti dostupan na locahost:5000/static/ a backend na locahost:5000/api/
   Primjer korištenja backenda je na localhost:5000/static/primjer_za_backend.html

## API dokumentacija

API služi za rad sa resursima web aplikacije (stvaranje novih i dohvat ili uređivanje postojećih), npr. stvaranje novog korisnika, dohvat objava koje je stvorio neki korisnik, komentara itd.

Argumenti se ovisno o zahtjevu šalju kao url query parametri ili u JSON formatu. Svi JSON odgovori koje vraća API pisani su u [JSend](https://github.com/omniti-labs/jsend) formatu.

U ostatku dokumentacije se pretpostavlja da je API dostupan na localhost:5000/

### Quickstart

1. Napravi novi korisnički račun:

   Na localhost:5000/api/users (HTTP metoda treba biti **POST**) poslati ovo:
   ```javascript
   {
     "username": "ime123",
     "password": "lozinka123"
     "email": "example@mail.com"
   }
   ```

   Email polje nije obavezno.

   Ovo je primjer JavaScript funkcije koja šalje zahtjev i ispisuje odgovor u konzolu.
   ```javascript
   async function register_user(uname, pass) {
     let url = "/api/users";
     let data = {username: uname,password: pass}
     try {
       let response = await fetch(url, {
         method: 'POST',
         body: JSON.stringify(data),
         headers: {
           'Content-Type': 'application/json'
         }
       });
       response = await response.json();
       console.log('Register response:', JSON.stringify(response));
       return response.success;
     } catch (error) {
       console.log('Error: ', error);
     }
   }
   ```

2. Ulogiraj se:

   Na localhost:5000/api/sesions (HTTP metoda treba biti **POST**) poslati ovo:
   ```javascript
   {
     "username": "ime123",
     "password": "lozinka123"
   }
   ```

   API vraća session cookie koji sadrži user id i koristi se za stvaranje resursa i kao dozvola za pristup postojećim.
 
3. Stvori novu objavu:

   Na localhost:5000/api/posts (HTTP metoda treba biti **POST**) poslati ovo:
   ```javascript
   {
     "title": "API design tips",
     "url": "https://medium.com/@petertboyer/learn-restful-api-design-ideals-c5ec915a430f?"
     "body": "An article with API design tips"
   }
   ```
 
   Naslov je obavezan, url i body nisu. (Objava može imati samo naslov, naslov i link, naslov i body ili sve)

4. Dohvati postojeće objave:

   Poslati zahtjev na localhost:5000/api/posts (HTTP metoda treba biti **GET**)

   Ovo je primjer odgovora koji se dobije:
   ```javascript
   {
     "data": [
       {
         "body": null,
         "created": "Fri, 13 Dec 2019 12:34:11 GMT",
         "edited": 0,
         "id": 2,
         "title": "ovo je google",
         "url": "google.com",
         "user_id": 2,
         "votes": 0
       },
       {
         "body": "aa",
         "created": "Fri, 13 Dec 2019 12:53:11 GMT",
         "edited": 1,
         "id": 3,
         "title": "uaaaaa",
         "url": null,
         "user_id": 2,
         "votes": 0
       }
     ],
     "status": "success"
   }
   ```
 
### Detaljniji opis cijelog API-ja

Glavni dijelovi API-ja su posts, comments, users i sessions. Općenito GET metoda služi za dohvat nekog resursa ili podresursa, POST za stvaranje novog, PATCH za update nekih vrijednosti, i DELETE za brisanje. Za stvaranje resursa (osim usera i session-a) treba biti ulogiran.

#### Users API

`GET`

Endpoint | Opis 
--- | --- 
/api/users/id | Dohvati korisnika po ID-u 
/api/users/id/posts | Dohvati objave nekog korisnika po njegovom ID-u, npr. /api/users/5/posts
/api/users/id/comments | Dohvati komentare nekog korisnika po ID-u  

`POST`

Endpoint | Opis | Argumenti (JSON)
--- | --- | ---
/api/users | Stvori novog korisnika | username, password, email (nije obavezan) 

`DELETE`

Endpoint | Opis
--- | --- 
/api/users | Obriši svoj korisnički račun (ID računa se pronađe u dobivenom session cookie-u. 

***

#### Sessions API

Služi za login i logout.

`POST`

Endpoint | Opis | Argumenti (JSON)
--- | --- | ---
/api/sessions | Stvori novi session (ulogiraj se). Korisniku se vraća potpisani session cookie koji sadrži njegov ID i koristi se za stvaranje resursa i kao dozvola za pristup postojećim. | username, password

`DELETE`

Endpoint | Opis
--- | --- 
/api/sessions | Prekini trenutni session (logout). Nakon slanja zahtjeva briše se korisnikov session cookie.

***

#### Posts API

`GET`

Endpoint | Opis | Argumenti (query parameters)
--- | --- | ---
/api/posts | Dohvati objave. Moguće ih je sortirati po starosti, rising i top. Očekuje se da će biti puno objava pa se ne dobivaju sve odjednom nego po stranicama. Način sortiranja i raspon traženih objava se određuje pomoću query parametara npr. /api/posts?page_size=20&page=2&sort_by=rising | page (default=1), page_size (default=20), sort_by (default=rising)
/api/posts/id | Dohvati jednu objavu po ID-u objave |
/api/posts/id/comments <img width=700/> | Dohvati komentare sve komentare na neku objavu |

`POST`

Endpoint | Opis | Argumenti (JSON)
--- | --- | ---
/api/posts | Stvori novu objavu | title, url (nije obavezan), body (nije obavezan)
/api/posts/id/comments | Stvori komentar na neku objavu. Komentar može biti odgovor na drugi komentar. | body (sadržaj komentara), parent_id (nije obavezno, ako parent_id postoji, novi komentar će bit odgovor na komentar koji ima poslani ID)
/api/posts/id/votes <img width=380/> | Stvori pozitivan ili negativan glas za neku objavu. | direction: 1 (positive) ili -1 (negative)

`PATCH`

Endpoint  | Opis | Argumenti (JSON)
--- | --- | --- 
/api/posts/id | Uredi sadržaj objave (body). Naslov i url se ne mogu urediti. | body

`DELETE`

Endpoint | Opis
--- | --- 
/api/posts/id | Obriši jednu od svojih objava

***

#### Comments API

`GET`

Endpoint | Opis 
--- | ---
/api/comments/id | Dohvati jedan komentar po ID-u 

`POST`

Endpoint | Opis | Argumenti (JSON)
--- | --- | ---
/api/comments/id/votes <img width=200/> | Stvori pozitivan ili negativan glas za neki komentar. | direction: 1 (positive) ili -1 (negative)

`PATCH`

Endpoint  | Opis | Argumenti (JSON)
--- | --- | --- 
/api/comments/id | Uredi sadržaj komentara (body) | body

`DELETE`

Endpoint | Opis
--- | --- 
/api/comments/id | Obriši jedan od svojih komentara
