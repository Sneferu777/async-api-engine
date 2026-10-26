# Asynchronous Data Extraction & Ingestion Engine

A high-performance asynchronous ETL pipeline built in Python using `asyncio`, `httpx`, `lxml`, and `sqlite3`. Engineered for concurrent DOM scraping, API ingestion, and multi-sink output persistence.

## Architectural Highlights

- **Decoupled Task Orchestration:** Producer-consumer pattern driven by non-blocking `asyncio.Queue` structures.
- **Bounded Request Throttling:** Network request rates managed via `asyncio.Semaphore` guards to prevent IP rate-limiting.
- **Resilient Network I/O:** Configurable worker-level retry routines featuring linear backoff logic.
- **Extensible Extraction Layer:** DOM parsing via `lxml` XPath selectors alongside structured JSON payload processing.
- **Persistence Sinks:** Transactional batch insertion into SQLite tables and streaming CSV generation.

## Repository Layout

```text
.
├── config.py    # Dataclass configuration engine defaults
├── engine.py    # Worker execution loop & retry logic
├── main.py      # Entry point & CLI orchestrator
├── parsers.py   # DOM (XPath) & JSON extraction parsers
├── sinks.py     # SQLite & CSV data persistence implementations
└── README.md    # Technical documentation
