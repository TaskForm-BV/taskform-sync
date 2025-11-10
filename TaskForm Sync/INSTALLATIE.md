# DataSync - Installatie & Configuratie Instructies

## 📋 Vereisten

- Windows 10 of hoger
- Toegang tot SQL Server en/of Firebird database
- API credentials (Base URL, API Key, Tenant ID)
- Administrator rechten voor Task Scheduler setup

---

## 🚀 Stap 1: Installatie

1. **Download** `DataSync.zip`
2. **Unzip** naar een vaste locatie, bijvoorbeeld:
   - `C:\DataSync`
   - `C:\Program Files\DataSync`
   - `D:\Apps\DataSync`

3. **Controleer** de bestanden:
   ```
   TaskForm Sync/
   ├── DataSync.exe          ✓
   ├── sync.exe              ✓
   ├── fbclient.dll          ✓ (voor Firebird)
   ├── config.template.json  ✓ (voorbeeld configuratie)
   ├── queries/              ✓
   └── logs/                 ✓
   ```

> ℹ️ **Let op:** Bij de eerste start wordt automatisch `config.json` aangemaakt vanuit de template.
> Bij updates blijft je `config.json` behouden en wordt alleen `config.template.json` overschreven.

> ℹ️ **Let op voor beheerders:** Python 3.13+ is vereist voor het bouwen van de applicatie.
> Het standaard installatiepad is `C:\Users\<gebruiker>\AppData\Local\Programs\Python\Python313\`.
> Gebruik het volledige pad naar `python.exe` wanneer je handmatig bouw- of testcommando's uitvoert.

---

## ⚙️ Stap 2: Configuratie

### Start de Configuratie Tool

1. **Dubbelklik** op `DataSync.exe`
2. Het configuratie scherm opent

### A. SQL Server Configuratie (optioneel)

**Als je SQL Server gebruikt:**

1. ☑️ **Check** "SQL Server inschakelen"

2. **Vul Connection String in:**

   **Voorbeeld - Windows Authentication:**
   ```
   Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=MijnDatabase;Trusted_Connection=yes;
   ```

   **Voorbeeld - SQL Authentication:**
   ```
   Driver={ODBC Driver 17 for SQL Server};Server=192.168.1.10;Database=MijnDatabase;UID=gebruiker;PWD=wachtwoord;
   ```

   **Voorbeeld - Named Instance:**
   ```
   Driver={ODBC Driver 17 for SQL Server};Server=SERVER\INSTANCE;Database=MijnDatabase;Trusted_Connection=yes;
   ```

3. **Klik** "Test SQL Server"
   - ✅ Groen = Werkt!
   - ❌ Rood = Check connection string

**Connection String Onderdelen:**
- `Server=` → Je database server (localhost, IP adres, of servernaam)
- `Database=` → Naam van je database
- `Trusted_Connection=yes` → Windows authenticatie
- `UID=` en `PWD=` → SQL authenticatie (gebruikersnaam & wachtwoord)

### B. Firebird Configuratie (optioneel)

**Als je Firebird gebruikt:**

1. ☑️ **Check** "Firebird inschakelen"

2. **Vul Database Pad in:**

   **Voorbeeld - Lokaal:**
   ```
   C:\Database\bedrijf.fdb
   ```

   **Voorbeeld - Netwerk:**
   ```
   \\SERVER\Share\database.fdb
   ```

   **Voorbeeld - Remote (IP):**
   ```
   192.168.1.100:C:\Database\bedrijf.fdb
   ```

3. **Username:** (meestal `SYSDBA`)
   ```
   SYSDBA
   ```

4. **Password:** Je database wachtwoord
   ```
   ********
   ```

5. **Klik** "Test Firebird"
   - ✅ Groen = Werkt!
   - ❌ Rood = Check pad en credentials

### C. API Configuratie (verplicht!)

**Vul je TaskForm API gegevens in:**

1. **Base URL:**
   ```
   https://api.taskform.nl/v1
   ```
   *(Vraag de juiste URL bij TaskForm)*

2. **X-Api-Key:** Je API sleutel
   ```
   tk_live_abc123def456ghi789...
   ```
   *(Vraag je API key bij TaskForm)*

3. **X-Tenant-ID:** Je organisatie/tenant ID
   ```
   12345
   ```
   *(Vraag je Tenant ID bij TaskForm)*

4. **Klik** "Test API"
   - ✅ Groen = API bereikbaar!
   - ❌ Rood = Check credentials

### D. Sync Instellingen

1. **Interval (minuten):**
   ```
   30
   ```
   *(Hoe vaak moet de sync draaien? Standaard elke 30 minuten)*

2. **Queries Map:**
   ```
   queries
   ```
   *(Laat staan tenzij je een andere locatie wilt)*

3. **Klik** "Opslaan & Sluiten"

**✅ Configuratie compleet!** Je `config.json` is nu aangemaakt.

---

## 📝 Stap 3: SQL Queries Toevoegen

### Query Bestanden Maken

1. **Open** de `queries` folder
2. **Maak** een nieuw `.sql` bestand voor elke tabel die je wilt synchroniseren

### Belangrijke Regels:

✅ **Bestandsnaam = API Table naam**
- `customers.sql` → Uploadt naar `/customers/bulk`
- `products.sql` → Uploadt naar `/products/bulk`
- `orders.sql` → Uploadt naar `/orders/bulk`

✅ **Query moet `external_id` kolom hebben**
- Dit is de unieke identifier voor upsert

### Voorbeeld Query: `customers.sql`

```sql
-- customers.sql
SELECT 
    CustomerID AS external_id,      -- VERPLICHT! Unieke ID
    CompanyName AS name,
    ContactName AS contact,
    Email,
    Phone,
    City,
    Country,
    GETDATE() AS last_sync           -- Optioneel: sync timestamp
FROM Customers
WHERE Active = 1                     -- Alleen actieve klanten
```

### Voorbeeld Query: `products.sql`

```sql
-- products.sql
SELECT 
    ProductID AS external_id,
    ProductName AS name,
    SKU,
    Price,
    StockQuantity AS stock,
    CategoryName AS category,
    LastModified
FROM Products
WHERE Discontinued = 0
```

### Tips voor Queries:

✅ **Gebruik AS voor kolomnamen** die de API verwacht
✅ **Filter** alleen relevante data (`WHERE Active = 1`)
✅ **Vermijd** `SELECT *` - kies specifieke kolommen
✅ **Test** je query eerst in SQL Management Studio
✅ **Let op** performantie bij grote tabellen

---

## 🧪 Stap 4: Testen

### Handmatig Testen

1. **Dubbelklik** `sync.exe`
2. Een console venster opent en toont:
   ```
   INFO - Starting sync at 2025-10-28 14:30:00
   INFO - Found 2 query files
   INFO - Processing query file: customers.sql -> table: customers
   INFO - SQL Server query executed successfully, 150 rows returned
   SUCCESS - Bulk upsert successful for customers: 150 records
   INFO - Processing query file: products.sql -> table: products
   INFO - SQL Server query executed successfully, 450 rows returned
   SUCCESS - Bulk upsert successful for products: 450 records
   INFO - Sync completed at 2025-10-28 14:30:15
   INFO - Duration: 15.32 seconds
   INFO - Successful: 2
   INFO - Failed: 0
   ```

3. **Check** de `logs` folder voor details:
   - `sync_20251028.log`
   - `api_20251028.log`
   - `sqlserver_20251028.log` (of `firebird_20251028.log`)

### Probleem Oplossen

**❌ "No data returned"**
→ Check of je query data terug geeft in je database tool

**❌ "API connection failed"**
→ Check Base URL, API Key en Tenant ID

**❌ "Database connection failed"**
→ Check connection string / Firebird credentials

**❌ "external_id not found"**
→ Je query moet een kolom `external_id` hebben (gebruik `AS external_id`)

---

## ⏰ Stap 5: Automatisch Draaien (Task Scheduler)

### Optie A: Via GUI (Makkelijkst)

1. **Open** Task Scheduler (zoek in Windows Start menu)

2. **Klik** "Create Basic Task"

3. **Naam:** `DataSync`
   **Beschrijving:** `Synchroniseert database naar TaskForm API`

4. **Trigger:** Daily
   - Start: Vandaag om 08:00
   - Recur every: 1 days
   - ☑️ **Advanced:** Repeat task every **30 minutes**
   - For a duration of: **Indefinitely**

5. **Action:** Start a program
   - **Program:** `C:\DataSync\sync.exe`
   - **Start in:** `C:\DataSync`

6. **Conditions tab:**
   - ☑️ Start only if computer is on AC power (voor laptops)
   - ☐ Stop if computer switches to battery power

7. **Settings tab:**
   - ☑️ Allow task to be run on demand
   - ☑️ If task fails, restart every: 1 minute, max 3 attempts

8. **Klik** Finish

### Optie B: Via PowerShell (Snel)

Open PowerShell **als Administrator** en run:

```powershell
$action = New-ScheduledTaskAction -Execute "C:\DataSync\sync.exe" -WorkingDirectory "C:\DataSync"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At 8am -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)).Repetition
Register-ScheduledTask -TaskName "DataSync" -Action $action -Trigger $trigger -Description "Synchroniseert database naar TaskForm API"
```

### Task Testen

**Start handmatig:**
1. Open Task Scheduler
2. Zoek "DataSync" task
3. Rechtermuisklik → **Run**
4. Check logs folder

**Status checken:**
- Task Scheduler → "DataSync" → History tab
- Bekijk "Last Run Result" (0x0 = success)

---

## 📊 Monitoring & Onderhoud

### Logs Controleren

**Dagelijks bekijken:**
```
logs/
├── sync_20251028.log       → Hoofdlog
├── api_20251028.log        → API calls
└── sqlserver_20251028.log  → Database queries
```

**Let op:**
- `SUCCESS` berichten = alles goed
- `WARNING` = mogelijk probleem
- `ERROR` = actie vereist

### Periodiek Onderhoud

**Wekelijks:**
- ✅ Check of sync nog draait (Task Scheduler)
- ✅ Bekijk logs op errors
- ✅ Controleer aantal records in API

**Maandelijks:**
- ✅ Verwijder oude logs (oudere dan 30 dagen)
- ✅ Check disk space
- ✅ Test nieuwe queries eerst handmatig

---

## 🆘 Support & Troubleshooting

### Veelvoorkomende Problemen

**Sync draait niet automatisch**
→ Check Task Scheduler, is task enabled?
→ Check user permissions

**Geen data in API**
→ Check logs voor errors
→ Test query handmatig in database tool
→ Controleer of `external_id` aanwezig is

**Firebird "fbclient.dll not found"**
→ Controleer of `fbclient.dll` in DataSync folder staat
→ Mogelijk Visual C++ 2005 Redistributable nodig

**SQL Server "Driver not found"**
→ Installeer "ODBC Driver 17 for SQL Server"
→ Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Contact

Voor hulp:
- 📧 Email: support@taskform.nl
- 📱 Check logs in `logs/` folder
- 🐛 GitHub: https://github.com/TaskForm-BV/taskform-sync/issues

---

## ✅ Checklist Installatie

- [ ] DataSync uitgepakt naar vaste locatie
- [ ] DataSync.exe geopend en geconfigureerd
- [ ] Database verbinding getest (groen vinkje)
- [ ] API verbinding getest (groen vinkje)
- [ ] SQL queries toegevoegd aan `queries/` folder
- [ ] Handmatig getest via sync.exe (succes in logs)
- [ ] Task Scheduler geconfigureerd
- [ ] Task handmatig getest (werkt automatisch)
- [ ] Logs gecontroleerd (geen errors)
- [ ] Eerste sync data zichtbaar in API

**🎉 Klaar! DataSync synchroniseert nu automatisch je database naar TaskForm!**