# DuckDB server, DuckDB-Wasm, and DuckDB 2.0

Research date: 2026-08-21

## Answer in brief

A DuckDB server plus DuckDB-Wasm client is useful when the application needs one authoritative, writable DuckDB instance shared by several processes or browsers. It is not the simpler default for read-only browser analytics over Parquet, CSV, JSON, or a downloadable DuckDB file. DuckDB-Wasm can query those sources in the browser without an application database server.

There is an important release boundary:

- The current stable DuckDB release is **1.5.5**, published on 2026-07-22.[1][2]
- DuckDB 2.0 is **announced but not released**. The release calendar lists 2.0.0 for "Fall 2026" and labels planned dates tentative. The 2.0 post calls itself a preview and says details may still change.[2][3]
- Stable DuckDB 1.5 already has a native client/server protocol, Quack, as a core extension starting in 1.5.3. It remains beta. DuckDB says the production release will arrive with 2.0.[4][5]
- This repository currently requires `duckdb<1.5.0`, so Duckalog does not currently admit any 1.5 release, including 1.5.3 where Quack became a core extension.[11]

The practical recommendation for Duckalog today is to keep the embedded architecture unless a concrete requirement calls for concurrent remote writers or a centrally managed live database. Treat a Quack deployment on 1.5.x as a beta experiment. Reassess it after 2.0 ships and Duckalog has tested and deliberately raised its DuckDB dependency bound.

## Release status

| Item | Status on 2026-08-21 | Evidence |
|---|---|---|
| Current stable DuckDB | 1.5.5 | GitHub marks v1.5.5 as a non-draft, non-prerelease release published 2026-07-22. The official calendar lists it as the latest past release.[1][2] |
| Current LTS line | 1.4.x, latest listed patch 1.4.5 | The release calendar labels 1.4 releases LTS and lists 1.4.5 on 2026-06-17.[2] |
| DuckDB 2.0 | Preview, planned for fall 2026 | The calendar places 2.0.0 under upcoming releases. The preview says "coming this fall" and warns that details may change.[2][3] |
| Quack in stable DuckDB | Available from 1.5.3, beta | The 1.5.3 announcement calls Quack a core extension, says it autoinstalls and autoloads, and explicitly labels it beta.[4] |
| DuckDB-Wasm engine base | 1.5.4 on the repository main branch at research time | The official DuckDB-Wasm README states that its current build is based on DuckDB 1.5.4.[7] |

"Current stable DuckDB" and "the DuckDB version embedded in the current DuckDB-Wasm build" are therefore not the same number. Native DuckDB is at 1.5.5 while the DuckDB-Wasm repository states 1.5.4.[1][7]

## What exists in stable DuckDB 1.5.x

### Embedded mode remains the normal architecture

DuckDB is an in-process database. A Python, C, Java, Node, or other host process loads DuckDB as a library and opens an in-memory database or database file. Historically there was no native server protocol. Separate processes could not safely modify the same DuckDB file concurrently because important state lives in each process.[5]

Quack adds network access without replacing this model. A DuckDB process loads the `quack` extension and calls `quack_serve`; another DuckDB instance attaches a `quack:` URI. Both ends run DuckDB.[5][6]

```sql
-- server-side DuckDB process
CALL quack_serve('quack:localhost', token = 'secret');

-- client-side DuckDB process
CREATE SECRET (TYPE quack, TOKEN 'secret');
ATTACH 'quack:localhost' AS remote;
SELECT * FROM remote.some_table;
```

Quack uses HTTP, defaults to port 9494, binds to localhost by default, and uses token authentication by default. DuckDB recommends an HTTPS-terminating reverse proxy rather than exposing a Quack endpoint directly to the internet.[5]

In 1.5.x, remote objects are exposed through `ATTACH`. The `remote.query(...)` function can send a complete query for remote execution when explicit pushdown is needed.[5] This matters because an attached remote catalog is not the same as a conventional thin client connection. The client still contains a DuckDB engine and participates in planning and data movement.

### What DuckDB-Wasm can do

DuckDB-Wasm compiles DuckDB to WebAssembly and runs it in the browser. It is a database engine in the client, not a JavaScript driver that must connect to a server. Its official repository states that it:

- returns and consumes Arrow data;
- reads Parquet, CSV, and JSON through browser filesystem APIs or HTTP;
- can read compatible DuckDB database files, including files attached from an HTTPS URL;
- supports a growing subset of core, community, and external extensions built specifically for WebAssembly;
- defaults to single-threaded execution, with multithreading still experimental.[7]

Browser rules remain part of the deployment. HTTP requests are upgraded to HTTPS and remote resources must permit the browser origin through CORS. DuckDB-Wasm uses a browser-specific HTTP implementation rather than the native `httpfs` extension.[7][9]

DuckDB-Wasm can load a WebAssembly build of the Quack extension. The Quack protocol deliberately uses HTTP so a browser-hosted DuckDB-Wasm instance can connect to a remote DuckDB server.[5][7][8] For an internet-facing setup, the official example places nginx and TLS in front of `quack_serve`.[8]

This gives two different browser architectures:

1. **Local browser analytics.** DuckDB-Wasm fetches files or object-store data and executes SQL in the browser.
2. **Remote DuckDB execution.** DuckDB-Wasm loads Quack, attaches a server, submits work to the remote DuckDB, and receives streamed results.

The second option does not turn DuckDB-Wasm into a lightweight generic SQL driver. The browser still downloads and initializes DuckDB-Wasm plus any required Wasm extensions.

### Extension limits in Wasm

Native DuckDB extensions are native binaries. DuckDB-Wasm extensions are separate Wasm binaries loaded through Emscripten. A native extension cannot simply be copied into a browser bundle.[9]

The official Wasm extension page lists a supported subset, including JSON, Parquet, ICU, SQLite, full-text search, and benchmark-related extensions. It also says `INSTALL` is a no-op in Wasm because there is no durable cross-session extension store; `LOAD` fetches, verifies, and loads the Wasm binary. Extension fetches and third-party repositories need CORS.[9]

The DuckDB-Wasm repository demonstrates Quack as a loadable Wasm extension, but the availability of an extension on native DuckDB does not prove that the same extension exists or has identical behavior on Wasm.[7][9]

## What DuckDB 2.0 is expected to change

The following items are announced preview behavior, not released guarantees.

### Server and client connectivity

Quack is planned to graduate from beta to stable in 2.0.[3][4] The preview introduces `CONNECT` and `DISCONNECT`:

```sql
ATTACH 'quack:server.example.com' AS qk (TOKEN 'my_token');
CONNECT qk;
SELECT count(*) FROM events;
DISCONNECT;
```

While connected, the query runs on the server and results stream back. The preview also says `CONNECT` will work with remote systems such as PostgreSQL and MySQL, with a remote pushdown optimizer sending SQL to the remote database instead of reading full tables into the local engine.[3]

Compared with 1.5.x, this is a clearer session-level server/client model. In stable 1.5.x, Quack uses `ATTACH` and may require `remote.query(...)` to force whole-query remote execution.[3][5]

### Database-file format

DuckDB 2.0 is planned to make storage format 2.0.0 the default. The preview names lazy column metadata, default `DICT_FSST` compression, more compact deletes, stronger corruption checks, and better checkpoint vacuuming for ART-indexed tables.[3]

DuckDB's storage compatibility policy says newer DuckDB versions can read database files produced by older versions covered by the compatibility guarantee. It does not make the reverse promise. A file written or checkpointed in the new 2.0 default format should not be treated as readable by a 1.5 engine or a DuckDB-Wasm build based on 1.5.4.[10]

For a native-server plus Wasm-client design, Quack avoids shipping the live database file to the browser. The server owns the file and sends query results. That is safer across engine-version differences than asking an older Wasm engine to open a newer file.

### Extension ABI and distribution

Today, many extensions build against DuckDB's unstable C++ API and must be rebuilt for each DuckDB release. The 2.0 preview describes a versioned C API specification, a stable ABI for a large part of that API, a thin C++ layer built on it, and support for custom signed extension repositories.[3]

This should reduce native extension rebuild churn. It does not erase the native-versus-Wasm platform split. Browser extensions will still need Wasm builds and browser-compatible behavior.[7][9]

### Other announced 2.0 changes relevant to a server

The preview also lists improved metrics and logging for long-running instances, asynchronous I/O, triggers, a new parser, and a new storage format.[3] These make a long-lived DuckDB service more plausible, but they do not by themselves provide clustering, replication, high availability, or managed operations. The Quack announcement describes replication as a future idea, not a current feature.[5]

## Catalog and database-file portability

These forms of portability are different:

### DuckDB database-file portability

A `.duckdb` file can carry tables, schemas, views, and metadata between compatible DuckDB engines. DuckDB-Wasm states that compatible DuckDB files can be read in the browser.[7] Version compatibility still applies.[10]

A file is not a network coordination protocol. Several processes should not independently open and modify the same file. Quack solves that use case by keeping one owning process and routing remote operations through it.[5]

### Catalog-definition portability

Duckalog defines catalogs in YAML or JSON and builds a DuckDB catalog through the Python API. Its architecture documentation describes configuration-driven creation of views, secrets, attachments, and external catalogs.[12] That declarative configuration is portable source material, but DuckDB-Wasm cannot run Duckalog itself because Duckalog is a Python package.

A generated database file may be readable by DuckDB-Wasm, but successful use also depends on everything referenced by the catalog:

- a view over HTTPS Parquet still needs CORS and browser-readable credentials;
- a native-only extension cannot load in Wasm;
- attached local paths from the server do not exist in the browser;
- secrets and environment-specific settings may be inappropriate to distribute inside a browser-readable file.

For Duckalog, the database file is therefore portable only when its sources and required extensions are portable too.

### Quack portability

Quack moves query execution to the environment that owns the catalog, paths, secrets, extensions, and database file. The browser receives results rather than the catalog's local runtime dependencies. This is the strongest reason to add a server when a Duckalog catalog depends on server-only resources.

## Fact-based architecture comparison

| Question | DuckDB-Wasm only | Native DuckDB plus Quack plus DuckDB-Wasm |
|---|---|---|
| Where SQL runs | Browser | Browser for local data; server for remote Quack work |
| Server required | No | Yes, a long-running DuckDB process calls `quack_serve` |
| Stable production protocol today | Not applicable | No. Quack is present in 1.5.x but beta |
| Concurrent writers to one authoritative DB | No shared browser-local database | Yes, through one server-owned DuckDB instance |
| Read Parquet/CSV/JSON over web | Yes, subject to HTTPS and CORS | Yes on either side; server can avoid browser CORS for server-side reads |
| Open DuckDB files | Yes, when format and referenced features are compatible | Server opens its file; client need not receive it |
| Native extension coverage | No, only Wasm-built subset | Server can use native extensions; client still has Wasm limits |
| Credentials | Must be safe to expose to browser, or use delegated access | Can remain on server |
| Browser download and compute | DuckDB-Wasm engine, extensions, data | DuckDB-Wasm engine and Quack extension, plus result data |
| Operational burden | Static hosting may be enough | Process supervision, TLS proxy, authentication, authorization, backups, upgrades |
| Current Duckalog compatibility | Duckalog can build an artifact, but does not run in browser | Duckalog's `<1.5.0` pin blocks the Quack core-extension release line |

## Recommendation for Duckalog

### Default now

Keep Duckalog as an embedded catalog builder and use DuckDB-Wasm directly for browser-local, read-heavy analytics when the catalog can be represented by browser-accessible files and Wasm-supported extensions. A DuckDB server adds no value merely because a browser client exists.

### Use a server when one of these requirements is real

A Quack server is a good fit when the application needs:

- concurrent writes from several processes or browsers into one DuckDB database;
- server-side credentials, local files, or native extensions that must not move to the browser;
- one live, authoritative catalog rather than downloadable snapshots;
- remote execution so large source data stays near the server and only results cross the network.

### Version decision

Do not describe DuckDB 2.0 capabilities as available today. On stable 1.5.5, Quack is usable but beta and its SQL and protocol may change. For a production Duckalog architecture, wait for the actual 2.0 release, then test:

1. Duckalog against the released 2.0 Python package;
2. Duckalog-generated files against the chosen DuckDB-Wasm build;
3. required native and Wasm extensions separately;
4. upgrade and rollback behavior for the 2.0 storage format;
5. Quack authentication, authorization, TLS proxying, and failure recovery.

If a server is needed before then, use the 1.5.x Quack path only with explicit acceptance of beta compatibility risk. Duckalog would first need a deliberate dependency update because its current constraint excludes 1.5.x.[11]

## Primary sources

1. DuckDB GitHub release, [DuckDB v1.5.5 Bugfix Release](https://github.com/duckdb/duckdb/releases/tag/v1.5.5), published 2026-07-22.
2. DuckDB documentation, [Release calendar](https://duckdb.org/release_calendar.html).
3. DuckDB blog, [A Preview of DuckDB v2.0](https://duckdb.org/2026/08/17/duckdb-20-highlights.html), 2026-08-17.
4. DuckDB release notes, [DuckDB v1.5.3](https://duckdb.org/2026/05/20/announcing-duckdb-153.html), 2026-05-20.
5. DuckDB blog, [Introducing the Quack Protocol for DuckDB](https://duckdb.org/2026/05/12/quack-remote-protocol.html), 2026-05-12.
6. Official Quack repository, [duckdb/duckdb-quack](https://github.com/duckdb/duckdb-quack).
7. Official DuckDB-Wasm repository, [duckdb/duckdb-wasm](https://github.com/duckdb/duckdb-wasm).
8. DuckDB documentation, [Quack on WebAssembly](https://duckdb.org/docs/current/quack/setup/quack_wasm.html).
9. DuckDB documentation, [DuckDB-Wasm extensions](https://duckdb.org/docs/current/clients/wasm/extensions.html).
10. DuckDB documentation, [Storage versions and format](https://duckdb.org/docs/current/internals/storage.html).
11. Duckalog source, [`pyproject.toml`, DuckDB dependency constraint](../../pyproject.toml#L42).
12. Duckalog documentation, [`docs/explanation/architecture.md`](../explanation/architecture.md).
