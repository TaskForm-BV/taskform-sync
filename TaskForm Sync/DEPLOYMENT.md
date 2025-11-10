# DataSync - Deployment Handleiding

## Portable Deployment (Geen Python installatie vereist)

Deze applicatie kan volledig portable worden gemaakt zodat eindgebruikers **geen Python** hoeven te installeren.

### Voorbereiding (Alleen voor ontwikkelaar)

1. **Installeer Python** (alleen op development machine):
   - Download Python 3.11+ van https://www.python.org/downloads/
   - Installeer met "Add to PATH" optie

2. **Installeer dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test de applicatie**:
   ```bash
   # Test GUI
   python gui.py
   
   # Test sync
   python sync.py
   ```

### Portable Executables Bouwen

Run het build script:
```bash
build_exe.bat
```

Dit maakt twee executables in de `dist` folder:
- `DataSync.exe` - GUI configuratie tool
- `sync.exe` - Sync service

### Deployment Package Maken

1. Maak een nieuwe folder, bijvoorbeeld: `DataSync-v1.0`

2. Kopieer de volgende bestanden/folders:
   ```
   DataSync-v1.0/
   ├── DataSync.exe       (van dist folder)
   ├── sync.exe           (van dist folder)
   ├── config.json        (leeg template)
   ├── queries/           (folder met example .sql files)
   │   ├── customers.sql
   │   └── products.sql
   └── logs/              (lege folder voor log files)
   ```

3. Zip de hele folder → `DataSync-v1.0.zip`

### Gebruikers Installatie

1. **Unzip** `DataSync-v1.0.zip` naar gewenste locatie (bijv. `C:\DataSync`)

2. **Run** `DataSync.exe` om de configuratie in te stellen:
   - Database verbindingen configureren
   - API settings invullen
   - Queries folder selecteren
   - Test alle verbindingen
   - Klik "Opslaan & Sluiten"

3. **Test** handmatig door `sync.exe` te draaien

4. **Configureer Windows Task Scheduler**:

   Open Command Prompt als Administrator:
   ```cmd
   schtasks /create /tn "DataSync" /tr "C:\DataSync\sync.exe" /sc minute /mo 30 /st 08:00 /et 18:00
   ```
   
   Of gebruik Task Scheduler GUI:
   - Open Task Scheduler
   - Create Basic Task
   - Name: "DataSync"
   - Trigger: Daily, repeat every 30 minutes
   - Action: Start program → Browse to `sync.exe`
   - Time range: 08:00 - 18:00 (werkuren)

### SQL Files Toevoegen

1. Plaats `.sql` bestanden in de `queries` folder
2. Bestandsnaam (zonder .sql) = API table naam
   - `customers.sql` → POST naar `/customers/bulk`
   - `products.sql` → POST naar `/products/bulk`
3. Query moet `external_id` kolom bevatten (of configureer `keyField`)

### Logging

Logs worden automatisch opgeslagen in `logs/` folder:
- `sync_YYYYMMDD.log` - Sync service logs
- `sqlserver_YYYYMMDD.log` - SQL Server logs
- `firebird_YYYYMMDD.log` - Firebird logs
- `api_YYYYMMDD.log` - API logs

### Troubleshooting

**Probleem**: `VCRUNTIME140.dll not found`
- **Oplossing**: Installeer Microsoft Visual C++ Redistributable
  https://aka.ms/vs/17/release/vc_redist.x64.exe

**Probleem**: Database drivers niet gevonden
- **Oplossing**: 
  - SQL Server: Installeer ODBC Driver for SQL Server
  - Firebird: Installeer Firebird client libraries

**Probleem**: Sync draait niet op geplande tijd
- **Oplossing**: Check Task Scheduler logs, controleer of user permissions correct zijn

### Updates

Om de applicatie te updaten:
1. Stop de Task Scheduler task
2. Vervang `DataSync.exe` en `sync.exe` met nieuwe versies
3. `config.json` wordt behouden (niet overschrijven!)
4. Herstart Task Scheduler task

### Advanced Build Opties

Voor een nog meer portable versie met embedded drivers:

```bash
# Inclusief alle dependencies en drivers
pyinstaller --onefile --add-data "drivers;drivers" gui.py
```

Zie `build_advanced.bat` voor meer opties.