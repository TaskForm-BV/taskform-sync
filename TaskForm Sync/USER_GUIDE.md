# DataSync - Gebruikershandleiding

**Versie 1.0** - Portable Windows Applicatie (Geen installatie vereist!)

## Wat is DataSync?

DataSync synchroniseert automatisch data van je SQL Server of Firebird database naar een API endpoint. Perfect voor het automatisch uploaden van klant-, product- of order-data.

## Snelstart (5 minuten)

### 1. Installatie
1. Download `DataSync.zip`
2. Unzip naar een lokatie (bijv. `C:\DataSync`)
3. Klaar! Geen Python of andere software nodig.

### 2. Configuratie
1. **Dubbelklik** op `DataSync.exe`
2. Vul de instellingen in:

   **Database** (kies er minimaal 1):
   - ☑️ SQL Server: Connection string invullen
   - ☑️ Firebird: Database pad, username, password

   **API Instellingen** (verplicht):
   - Base URL: bijv. `https://api.example.com/v1`
   - API Key: je API sleutel
   - Tenant ID: je tenant/organisatie ID

   **Sync Instellingen**:
   - Interval: hoe vaak (in minuten) moet de sync draaien
   - Queries Map: waar staan je SQL bestanden (standaard: `queries`)

3. **Test** elke verbinding met de "Test" knoppen
4. **Klik** "Opslaan & Sluiten"

### 3. SQL Queries Toevoegen

Plaats je SQL queries in de `queries` folder:

**Belangrijk**: 
- Bestandsnaam = API table naam (zonder `.sql`)
- Query moet `external_id` kolom hebben

**Voorbeeld** - `queries/customers.sql`:
```sql
SELECT 
    id AS external_id,
    name,
    email,
    phone
FROM customers
WHERE active = 1
```

Dit synchroniseert naar: `https://api.example.com/v1/customers/bulk`

### 4. Test de Sync

Dubbelklik op `sync.exe` om handmatig te testen. 

Controleer de `logs` folder voor resultaten.

### 5. Automatische Sync (Optioneel)

Om elke 30 minuten automatisch te synchroniseren:

**Methode 1: Task Scheduler GUI**
1. Open Windows Task Scheduler
2. Klik "Create Basic Task"
3. Naam: `DataSync`
4. Trigger: Daily, repeat every 30 minutes
5. Action: Start program → `C:\DataSync\sync.exe`
6. Klaar!

**Methode 2: Command Line** (als Administrator)
```cmd
schtasks /create /tn "DataSync" /tr "C:\DataSync\sync.exe" /sc minute /mo 30
```

## Hoe werkt het?

```
┌─────────────┐         ┌──────────┐         ┌─────────┐
│  Database   │ ──SQL──▶│  sync.exe │ ──API──▶│   API   │
│ SQL/Firebird│         │          │         │Endpoint │
└─────────────┘         └──────────┘         └─────────┘
                             │
                             ▼
                        ┌─────────┐
                        │  Logs   │
                        └─────────┘
```

1. `sync.exe` leest `config.json`
2. Voor elk `.sql` bestand in `queries/`:
   - Voert query uit op database
   - Stuurt resultaten naar API als bulk upsert
   - Logt resultaten
3. Klaar!

## Bestanden & Folders

```
DataSync/
├── DataSync.exe       → GUI configuratie tool
├── sync.exe           → Sync service (automatisch of handmatig)
├── config.json        → Instellingen (automatisch aangemaakt)
├── queries/           → Je SQL bestanden
│   ├── customers.sql
│   └── products.sql
└── logs/              → Log bestanden
    ├── sync_20231028.log
    ├── api_20231028.log
    └── ...
```

## Veelgestelde Vragen

**Q: Moet ik Python installeren?**  
A: Nee! De executables bevatten alles wat nodig is.

**Q: Kan ik meerdere databases tegelijk gebruiken?**  
A: Ja, schakel zowel SQL Server als Firebird in. De sync probeert eerst SQL Server, daarna Firebird.

**Q: Hoe vaak kan ik synchroniseren?**  
A: Zo vaak je wilt, maar wees redelijk (minimaal 1 minuut aanbevolen).

**Q: Wat als een sync faalt?**  
A: De sync probeert automatisch 3x met exponential backoff. Check de logs voor details.

**Q: Kan ik custom queries maken?**  
A: Ja! Maak gewoon een nieuw `.sql` bestand in `queries/`. De bestandsnaam bepaalt de API endpoint.

**Q: Welke SQL database wordt gebruikt?**  
A: Als beide zijn ingeschakeld, probeert sync eerst SQL Server, dan Firebird.

## Support

Problemen? Check de logs in `logs/` folder. Elke service heeft zijn eigen log file met timestamps.

Voor bugs of feature requests: https://github.com/TaskForm-BV/taskform-sync/issues

---

**Made with ❤️ for TaskForm**