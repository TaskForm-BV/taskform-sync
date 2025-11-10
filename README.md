# DataSync Tool

Een Python applicatie voor het periodiek synchroniseren van SQL data naar een API endpoint.

## Componenten

- **DataSync.exe**: GUI configuratietool en launcher (Tkinter)
- **sync.exe**: Headless sync-service voor Windows Task Scheduler
- **config.json**: Configuratiebestand
- **queries/**: Map met SQL-bestanden
- **logs/**: Map met logbestanden

## Features

- SQL Server en Firebird database ondersteuning
- GUI voor configuratie met test functies
- Bulk API upload met upsert operatie
- Configureerbare sync intervallen
- Logging en error handling
- Retry logic met exponential backoff
- Portable deployment (geen Python installatie vereist)

## Installatie

1. Download de release
2. Unzip naar gewenste locatie
3. Run `DataSync.exe` voor configuratie
4. Setup Windows Task Scheduler voor `sync.exe`

## Gebruik

### GUI Configuratie
- Start `DataSync.exe`
- Configureer database verbindingen
- Test verbindingen
- Configureer API settings
- Selecteer queries folder
- Sla configuratie op

### Sync Service
- Run `sync.exe` handmatig of via Task Scheduler
- Controleert config.json
- Voert SQL queries uit
- Upload naar API endpoint
- Logt resultaten

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python gui.py

# Run sync
python sync.py

# Build deployment package (recommended)
build_advanced.bat

# Or build executables only
build_exe.bat
```

### Build Scripts

- **`build_advanced.bat`** (aanbevolen) - Complete deployment package met ZIP
- **`build_exe.bat`** - Alleen executables bouwen
- **`build_clean.bat`** - Deprecated, gebruik build_advanced.bat

## Project Structuur

```
datasync/
├── gui.py                 # GUI applicatie
├── sync.py                # Sync service
├── config.py              # Configuratie helper
├── services/
│   ├── __init__.py
│   ├── sqlserver_service.py
│   ├── firebird_service.py
│   └── api_service.py
├── utils/
│   ├── __init__.py
│   └── logging.py
├── queries/               # SQL bestanden
│   └── example.sql
├── logs/                  # Log bestanden
├── config.json           # Configuratie
├── requirements.txt
├── build_exe.bat         # Build script
└── README.md
```