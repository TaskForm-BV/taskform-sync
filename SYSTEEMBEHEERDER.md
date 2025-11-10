# TaskForm Sync - Informatie voor Systeembeheerders

## Wat doet deze applicatie?

TaskForm Sync is een **data synchronisatie tool** die periodiek data uit jullie databases (Firebird of SQL Server) ophaalt en naar onze cloud API stuurt. Dit maakt realtime integratie mogelijk tussen jullie systemen en het TaskForm platform.

## Hoe werkt het?

1. **Query's uitvoeren**: De tool leest `.sql` bestanden uit een `queries` folder en voert deze uit op jullie database
2. **Data transformeren**: Resultaten worden omgezet naar JSON formaat
3. **Verzenden naar API**: Data wordt via HTTPS POST verstuurd naar onze beveiligde API endpoints
4. **Logging**: Alle acties worden lokaal gelogd voor audit doeleinden

## Technische details

- **Executable**: `sync.exe` (Windows, geen Python of dependencies vereist)
- **Connectie**: Uitgaande HTTPS verbindingen naar TaskForm API (poort 443)
- **Authenticatie**: API key in configuratiebestand
- **Database toegang**: Read-only queries (SELECT statements)
- **Scheduling**: Via Windows Task Scheduler (standaard elk half uur tijdens werkuren)

## Beveiligingsaspecten

### ✅ Veilig
- **Read-only database toegang**: Alleen SELECT queries, geen wijzigingen aan jullie data mogelijk
- **Encrypted credentials**: Database wachtwoorden en API keys worden encrypted opgeslagen
- **HTTPS communicatie**: Alle API calls zijn versleuteld (TLS 1.2+)
- **Lokale logging**: Logs blijven lokaal op de server
- **Geen inbound connecties**: Tool maakt alleen uitgaande verbindingen naar onze API
- **Dry-run modus**: Test zonder data te versturen

### ⚠️ Aandachtspunten
- **Database credentials**: Tool heeft (read-only) toegang tot jullie database nodig
- **Netwerk toegang**: Uitgaande HTTPS naar `[jullie-api-endpoint]` moet toegestaan zijn
- **API key opslag**: Gevoelige informatie in `config.json` - beveilig met NTFS permissions
- **Task Scheduler**: Draait onder een Windows gebruikersaccount met database toegang

## Benodigde resources

- **Disk space**: ~50 MB voor applicatie + logs
- **Memory**: ~100 MB tijdens uitvoering
- **CPU**: Minimaal (enkele seconden per sync cyclus)
- **Network**: < 1 MB per sync (afhankelijk van dataset grootte)

## Benodigde toegang

### Database
- Read-only toegang tot specifieke tabellen/views
- Of: dedicated read-only database gebruiker aanmaken (aanbevolen)

### Netwerk
- **Uitgaand HTTPS**: `[jullie-api-endpoint]` op poort 443
- **Geen firewall regels nodig**: Alleen standaard uitgaande HTTPS

### Filesystem
- **Installatiemap**: Lees/schrijf rechten (bijv. `C:\TaskForm Sync\`)
- **Logs folder**: Schrijf rechten voor logging
- **Config file**: Lees rechten (bevat credentials)

## Installatie locatie (aanbeveling)

```
C:\TaskForm Sync\
├── sync.exe              (hoofdprogramma)
├── DataSync.exe          (optioneel: GUI configuratie tool)
├── config.json           (configuratie met credentials)
├── queries\              (SQL query bestanden)
├── logs\                 (applicatie logs)
└── fbclient.dll          (alleen voor Firebird databases)
```

## Monitoring

**Logs locatie**: `C:\TaskForm Sync\logs\`
- `sync_YYYYMMDD.log` - Sync resultaten en errors
- `api_YYYYMMDD.log` - API communicatie
- `firebird_YYYYMMDD.log` of `sqlserver_YYYYMMDD.log` - Database queries

## Upload volgorde instellen

- Bepaal de volgorde van uploads via `sync.query_order` in `config.json`
- Gebruik bestandsnamen zoals `customers.sql`; extensie wordt automatisch toegevoegd als je alleen de basisnaam opgeeft
- Bestanden die niet genoemd worden, draaien alfabetisch na de opgegeven lijst
- Onjuiste of ontbrekende bestandsnamen worden gelogd als waarschuwing

**Success indicatoren**:
- Log toont "Sync completed successfully"
- Geen ERROR entries in logs
- Task Scheduler toont "Last Run Result: Success"

**Troubleshooting**:
- Check logs bij problemen
- Test handmatig door `sync.exe` te draaien vanuit command prompt
- Gebruik `DataSync.exe` GUI om database/API connecties te testen

## Risico analyse

| Risico | Impact | Waarschijnlijkheid | Mitigatie |
|--------|--------|-------------------|-----------|
| Database overbelasting | Laag | Laag | Read-only queries, max 1x per 30 min |
| Data exposure | Gemiddeld | Laag | HTTPS encryptie, beveiligde API |
| Credential theft | Gemiddeld | Laag | Encrypted opslag, NTFS permissions |
| Service verstoring | Laag | Laag | Draait apart van core systemen |

## Aanbevolen security hardening

1. **Database user**: Maak dedicated read-only account aan voor sync tool
2. **File permissions**: Beperk `config.json` toegang tot sync service account
3. **Network**: Optioneel: Whitelist alleen uitgaand verkeer naar TaskForm API IP's
4. **Monitoring**: Configureer alerting op sync failures (via Windows Event Log)
5. **Audit**: Review logs periodiek voor onverwacht gedrag

## Vragen of problemen?

Voor technische support:
- **Email**: support@taskform.nl
- **Documentatie**: Zie `README.md`, `DEPLOYMENT.md`, `USER_GUIDE.md` in de installatiemap
- **Logs**: Altijd beschikbaar in `logs\` folder voor troubleshooting

---

**Versie**: 2.0  
**Laatst bijgewerkt**: November 2025  
**Contact**: TaskForm B.V.
