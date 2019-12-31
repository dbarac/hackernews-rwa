# hackernews clone projekt za RWA

## Opis

Korisnici objavljuju linkove za koje drugi korisnici glasaju. Na početnoj stranici objave mogu biti rangirane po starosti, top, ili rising. Korisnici mogu komentirati objave, odgovarati na komentare, uređivati svoje komentare i glasati za druge komentare. Za svakog korisnika se mogu dohvatiti njegove objave i komentari.

## Instalacija

ovo treba napisat

## API dokumentacija

API služi za rad sa resursima web aplikacije (stvaranje novih i dohvat ili uređivanje postojećih), npr. stvaranje novog korisnika, dohvat objava koje je stvorio neki korisnik, komentara itd.

Argumenti se ovisno o zahtjevu šalju kao url query parametri ili u JSON formatu. Svi odgovori koje vraća API pisani su u [JSend](https://github.com/omniti-labs/jsend) formatu.

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
