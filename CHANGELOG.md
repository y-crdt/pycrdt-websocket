# Version history

## 0.16.0

- Allow room to sync with provider.
- Add `log` to `BaseYStore`.
- Handle ASGI lifespan.
- Move `test` and `docs` dependencies to dependency groups.
- Extract out stores to `pycrdt-store`.

## 0.15.5

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.15.4...8c2285fafc7dbeee92d3d87b40c0f591edee4445))

### Bugs fixed

- Avoid propagating disconnection message from client [#118](https://github.com/jupyter-server/pycrdt-websocket/pull/118) ([@brichet](https://github.com/brichet))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2025-01-23&to=2025-04-15&type=c))

[@brichet](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Abrichet+updated%3A2025-01-23..2025-04-15&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2025-01-23..2025-04-15&type=Issues)

## 0.15.4

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.15.3...4c9f21a9e75d7f726f293674abee820837e44ea7))

### Maintenance and upkeep improvements

- Increase pycrdt compatible version range [#104](https://github.com/jupyter-server/pycrdt-websocket/pull/104) ([@fcollonval](https://github.com/fcollonval))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-12-10&to=2025-01-23&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-12-10..2025-01-23&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Afcollonval+updated%3A2024-12-10..2025-01-23&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-12-10..2025-01-23&type=Issues)

## 0.15.3

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.15.2...3a74f65bd4d0e27634ec035699828e1cf80bd036))

### Documentation improvements

- Update client/server examples [#95](https://github.com/jupyter-server/pycrdt-websocket/pull/95) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-12-10&to=2024-12-10&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-12-10..2024-12-10&type=Issues)

## 0.15.2

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.15.1...d208ff03390d17e0dc3e438e39d0af150b3f7d93))

### Bugs fixed

- Remove client on failure [#94](https://github.com/jupyter-server/pycrdt-websocket/pull/94) ([@darabos](https://github.com/darabos))

### Maintenance and upkeep improvements

- Dead code [#89](https://github.com/jupyter-server/pycrdt-websocket/pull/89) ([@fcollonval](https://github.com/fcollonval))

### Documentation improvements

- Update client documentation [#91](https://github.com/jupyter-server/pycrdt-websocket/pull/91) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-10-14&to=2024-12-10&type=c))

[@darabos](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adarabos+updated%3A2024-10-14..2024-12-10&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-10-14..2024-12-10&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Afcollonval+updated%3A2024-10-14..2024-12-10&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-10-14..2024-12-10&type=Issues)

## 0.15.1

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.15.0...b43acfd307f4af68efc6bc460e9e597748cdf59e))

### Enhancements made

- Start the server awareness [#78](https://github.com/jupyter-server/pycrdt-websocket/pull/78) ([@brichet](https://github.com/brichet))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-10-09&to=2024-10-14&type=c))

[@brichet](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Abrichet+updated%3A2024-10-09..2024-10-14&type=Issues)

## 0.15.0

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.14.3...e361683b4752cedce933c362c510e40302865dc4))

### Enhancements made

- Broadcast server awareness to all clients [#73](https://github.com/jupyter-server/pycrdt-websocket/pull/73) ([@brichet](https://github.com/brichet))

### Bugs fixed

- Apply awareness updates to server awareness [#76](https://github.com/jupyter-server/pycrdt-websocket/pull/76) ([@davidbrochart](https://github.com/davidbrochart))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-10-04&to=2024-10-09&type=c))

[@brichet](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Abrichet+updated%3A2024-10-04..2024-10-09&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-10-04..2024-10-09&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-10-04..2024-10-09&type=Issues)

## 0.14.3

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.14.2...04d5eb3ce82e5677890c88540d8da8f7e3d6821a))

### Maintenance and upkeep improvements

- Remove the awareness in favor of the one from pycrdt [#74](https://github.com/jupyter-server/pycrdt-websocket/pull/74) ([@brichet](https://github.com/brichet))
- Update GitHub actions [#72](https://github.com/jupyter-server/pycrdt-websocket/pull/72) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-08-29&to=2024-10-04&type=c))

[@brichet](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Abrichet+updated%3A2024-08-29..2024-10-04&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-08-29..2024-10-04&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-08-29..2024-10-04&type=Issues)

## 0.14.2

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.14.1...713f53930d61d3a8869dbbf75801c0f082b538ff))

### Enhancements made

- Allow passing a ydoc to a room [#66](https://github.com/jupyter-server/pycrdt-websocket/pull/66) ([@davidbrochart](https://github.com/davidbrochart))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-07-05&to=2024-08-29&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-07-05..2024-08-29&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-07-05..2024-08-29&type=Issues)

## 0.14.1

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.14.0...de03fb95ca18c4fe548eaef0250d1f6cbb0594df))

### Maintenance and upkeep improvements

- Bump pycrdt >=0.9.0 [#56](https://github.com/jupyter-server/pycrdt-websocket/pull/56) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-06-25&to=2024-07-05&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-06-25..2024-07-05&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-06-25..2024-07-05&type=Issues)

## 0.14.0

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.5...39ebb2981ef80bbaa867a013675f30091c69535c))

### Maintenance and upkeep improvements

- Use pycrdt v0.8.30 [#54](https://github.com/jupyter-server/pycrdt-websocket/pull/54) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-06-11&to=2024-06-25&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-06-11..2024-06-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-06-11..2024-06-25&type=Issues)

## 0.13.5

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.4...d425e26360a00ff78dda12317756f3578b362c7b))

### Enhancements made

- Use sqlite-anyio's Connection async context manager and exception logger [#51](https://github.com/jupyter-server/pycrdt-websocket/pull/51) ([@davidbrochart](https://github.com/davidbrochart))

### Maintenance and upkeep improvements

- Add undo manager test [#48](https://github.com/jupyter-server/pycrdt-websocket/pull/48) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-05-07&to=2024-06-11&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-05-07..2024-06-11&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-05-07..2024-06-11&type=Issues)

## 0.13.4

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.3...63cd8a6ee9ba35a2e15aba89da11e080a480dd58))

### Enhancements made

- Wait for ystore to be started [#43](https://github.com/jupyter-server/pycrdt-websocket/pull/43) ([@davidbrochart](https://github.com/davidbrochart))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-05-06&to=2024-05-07&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-05-06..2024-05-07&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-05-06..2024-05-07&type=Issues)

## 0.13.3

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.2...e13521d503e4858dac4db78d7f61e8010596ad35))

### Enhancements made

- Keep the YStore task group alive [#42](https://github.com/jupyter-server/pycrdt-websocket/pull/42) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-05-02&to=2024-05-06&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-05-02..2024-05-06&type=Issues)

## 0.13.2

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.1...8e85b261a65e31aa5a50280e3b65e2be05039ce2))

### Bugs fixed

- fix ystore start flow [#40](https://github.com/jupyter-server/pycrdt-websocket/pull/40) ([@jzhang20133](https://github.com/jzhang20133))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-04-29&to=2024-05-02&type=c))

[@jzhang20133](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Ajzhang20133+updated%3A2024-04-29..2024-05-02&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-04-29..2024-05-02&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3AZsailer+updated%3A2024-04-29..2024-05-02&type=Issues)

## 0.13.1

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.13.0...c501156c7c5e6dbb78daf48af97a3a48903c6f06))

### Enhancements made

- adding exception handling for room start tasks [#33](https://github.com/jupyter-server/pycrdt-websocket/pull/33) ([@jzhang20133](https://github.com/jzhang20133))

### Maintenance and upkeep improvements

- Add Releaser Github Actions [#37](https://github.com/jupyter-server/pycrdt-websocket/pull/37) ([@Zsailer](https://github.com/Zsailer))

### Other merged PRs

- Fix room async context manager [#35](https://github.com/jupyter-server/pycrdt-websocket/pull/35) ([@davidbrochart](https://github.com/davidbrochart))
- Don't use mypy v1.10.0 [#32](https://github.com/jupyter-server/pycrdt-websocket/pull/32) ([@davidbrochart](https://github.com/davidbrochart))
- Add WebsocketServer exception handler [#31](https://github.com/jupyter-server/pycrdt-websocket/pull/31) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-04-25&to=2024-04-29&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-04-25..2024-04-29&type=Issues) | [@jzhang20133](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Ajzhang20133+updated%3A2024-04-25..2024-04-29&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Awelcome+updated%3A2024-04-25..2024-04-29&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3AZsailer+updated%3A2024-04-25..2024-04-29&type=Issues)

## 0.13.0

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.12.7...3f9cd15b2bec45db9b061f380044dcd1023bf0e3))

### Merged PRs

- Rework how services are started/stopped [#24](https://github.com/jupyter-server/pycrdt-websocket/pull/24) ([@davidbrochart](https://github.com/davidbrochart))
- Replace aiosqlite with sqlite-anyio [#22](https://github.com/jupyter-server/pycrdt-websocket/pull/22) ([@davidbrochart](https://github.com/davidbrochart))
- Fix documentation link [#20](https://github.com/jupyter-server/pycrdt-websocket/pull/20) ([@davidbrochart](https://github.com/davidbrochart))
- Remove warning about project not ready for production [#17](https://github.com/jupyter-server/pycrdt-websocket/pull/17) ([@davidbrochart](https://github.com/davidbrochart))
- Drop YTest [#14](https://github.com/jupyter-server/pycrdt-websocket/pull/14) ([@davidbrochart](https://github.com/davidbrochart))
- Add contributing documentation [#12](https://github.com/jupyter-server/pycrdt-websocket/pull/12) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2024-01-30&to=2024-04-25&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2024-01-30..2024-04-25&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adlqqq+updated%3A2024-01-30..2024-04-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2024-01-30..2024-04-25&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Awelcome+updated%3A2024-01-30..2024-04-25&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3AZsailer+updated%3A2024-01-30..2024-04-25&type=Issues)

## 0.12.7

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.12.6...ded67cd3e51f7db7ea8b8fb4442366a3f6ea2755))

### Merged PRs

- Switch to ruff-format [#10](https://github.com/jupyter-server/pycrdt-websocket/pull/10) ([@davidbrochart](https://github.com/davidbrochart))
- Set project status to incubating [#4](https://github.com/jupyter-server/pycrdt-websocket/pull/4) ([@Zsailer](https://github.com/Zsailer))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2023-12-26&to=2024-01-30&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2023-12-26..2024-01-30&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Awelcome+updated%3A2023-12-26..2024-01-30&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3AZsailer+updated%3A2023-12-26..2024-01-30&type=Issues)

## 0.12.6

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/v0.12.5...b4a55efb4eb3f9fc5191c18cbcb627129677fb10))

### Merged PRs

- Update pycrdt v0.8 [#7](https://github.com/jupyter-server/pycrdt-websocket/pull/7) ([@davidbrochart](https://github.com/davidbrochart))
- Fix README [#2](https://github.com/jupyter-server/pycrdt-websocket/pull/2) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2023-12-08&to=2023-12-26&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2023-12-08..2023-12-26&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Apre-commit-ci+updated%3A2023-12-08..2023-12-26&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Awelcome+updated%3A2023-12-08..2023-12-26&type=Issues)

## 0.12.5

([Full Changelog](https://github.com/jupyter-server/pycrdt-websocket/compare/de210d3a945eebd8cfb7907f7b10265ffc907fe1...5de0c0e3604e3b03ef396af29c0a9dc5f5425ffe))

### Merged PRs

- Replace davidbrochart with jupyter-server [#1](https://github.com/jupyter-server/pycrdt-websocket/pull/1) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/pycrdt-websocket/graphs/contributors?from=2022-04-21&to=2023-12-08&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Adavidbrochart+updated%3A2022-04-21..2023-12-08&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fpycrdt-websocket+involves%3Awelcome+updated%3A2022-04-21..2023-12-08&type=Issues)

## 0.12.4

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.12.3...5e95afd99fcc5373591876f2023b975e18fad3cb))

### Merged PRs

- Fix \_staring -> \_starting [#87](https://github.com/y-crdt/ypy-websocket/pull/87) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-09-07&to=2023-10-04&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-09-07..2023-10-04&type=Issues)

## 0.12.3

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.12.2...18a479d012a880981e6d31d71269468abff75cfe))

### Merged PRs

- Add Django Channels consumer [#84](https://github.com/y-crdt/ypy-websocket/pull/84) ([@zswaff](https://github.com/zswaff))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-08-31&to=2023-09-07&type=c))

[@zswaff](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Azswaff+updated%3A2023-08-31..2023-09-07&type=Issues)

## 0.12.2

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.12.1...214b8365ccd38cd620e6f5b46d34354bdd3d8dbf))

### Merged PRs

- Pin anyio\<5 [#83](https://github.com/y-crdt/ypy-websocket/pull/83) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-06-20&to=2023-08-31&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-06-20..2023-08-31&type=Issues)

## 0.12.1

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.12.0...930ec4956bea9954b7ce06acfa66629a0273736f))

### Merged PRs

- Install typing_extensions for python\<3.8 [#82](https://github.com/y-crdt/ypy-websocket/pull/82) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-06-20&to=2023-06-20&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-06-20..2023-06-20&type=Issues)

## 0.12.0

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.11.1...1af218b034ac16d1bd20d53230e83c9570a799be))

### Merged PRs

- Start store from room, start room from server [#81](https://github.com/y-crdt/ypy-websocket/pull/81) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-06-19&to=2023-06-20&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-06-19..2023-06-20&type=Issues)

## 0.11.1

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.11.0...55b5fb6032b8ee03f41601ea130f6eb5d29edcf2))

### Merged PRs

- Type get_room as possible coroutine [#80](https://github.com/y-crdt/ypy-websocket/pull/80) ([@davidbrochart](https://github.com/davidbrochart))
- Fix documentation link [#79](https://github.com/y-crdt/ypy-websocket/pull/79) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-06-16&to=2023-06-19&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-06-16..2023-06-19&type=Issues)

## 0.11.0

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.10.0...17a2e147b34dea8b46ced173417df1f386d957ee))

### Merged PRs

- Use AnyIO [#77](https://github.com/y-crdt/ypy-websocket/pull/77) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-06-01&to=2023-06-16&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-06-01..2023-06-16&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Afcollonval+updated%3A2023-06-01..2023-06-16&type=Issues)

## 0.10.0

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.9.0...49a45305416f70a5c7c969f1017e5b3e871db812))

### Merged PRs

- Implement ASGI server [#75](https://github.com/y-crdt/ypy-websocket/pull/75) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-04-06&to=2023-06-01&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-04-06..2023-06-01&type=Issues)

## 0.9.0

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.8.4...69cbc95f011e29418cd2c0904245db16b7b0fb64))

### Merged PRs

- Use anyio instead of aiofiles [#72](https://github.com/y-crdt/ypy-websocket/pull/72) ([@davidbrochart](https://github.com/davidbrochart))
- Add license, URLs, classifiers [#71](https://github.com/y-crdt/ypy-websocket/pull/71) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-02-21&to=2023-04-06&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-02-21..2023-04-06&type=Issues)

## 0.8.4

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.8.3...7b7f66d380e5ff02d4dceb51d5a16bd6fc3adc76))

### Merged PRs

- Keep reference to asyncio tasks [#69](https://github.com/y-crdt/ypy-websocket/pull/69) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2023-02-20&to=2023-02-21&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2023-02-20..2023-02-21&type=Issues)

## 0.8.3

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.8.2...f0851d01bd7143bf5b94a0dbf90120aac0bd2800))

### Merged PRs

- Bump y-py >=0.6.0,\<0.7.0 [#68](https://github.com/y-crdt/ypy-websocket/pull/68) ([@davidbrochart](https://github.com/davidbrochart))
- Move pytest.ini entries to pyproject.toml [#64](https://github.com/y-crdt/ypy-websocket/pull/64) ([@bnavigator](https://github.com/bnavigator))
- Compare dicts not JSON string with dicts [#63](https://github.com/y-crdt/ypy-websocket/pull/63) ([@bnavigator](https://github.com/bnavigator))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2022-12-06&to=2023-02-20&type=c))

[@bnavigator](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Abnavigator+updated%3A2022-12-06..2023-02-20&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2022-12-06..2023-02-20&type=Issues)

## 0.8.2

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.8.1...6409366bb86e80e22a04e7b7933a5ce5dd84b77e))

### Merged PRs

- Use a lock in SQLiteYStore [#61](https://github.com/y-crdt/ypy-websocket/pull/61) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2022-12-01&to=2022-12-06&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2022-12-01..2022-12-06&type=Issues)

## 0.8.1

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.8.0...433868106d79df11c822f8f99f1f1f30a33d4974))

### Merged PRs

- Set package as typed [#60](https://github.com/y-crdt/ypy-websocket/pull/60) ([@davidbrochart](https://github.com/davidbrochart))
- Ignore empty updates [#59](https://github.com/y-crdt/ypy-websocket/pull/59) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2022-11-25&to=2022-12-01&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2022-11-25..2022-12-01&type=Issues) | [@ellisonbg](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Aellisonbg+updated%3A2022-11-25..2022-12-01&type=Issues)

## 0.8.0

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/v0.7.2...93695bb8506b47ff88f3e36c4f5fc4823e650513))

### Merged PRs

- Implement timestamp in FileYStore, return timestamp in read [#57](https://github.com/y-crdt/ypy-websocket/pull/57) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2022-11-25&to=2022-11-25&type=c))

[@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2022-11-25..2022-11-25&type=Issues)

## 0.7.2

([Full Changelog](https://github.com/y-crdt/ypy-websocket/compare/0.7.0...6f15b90fac8105e9b0ef369df30ca08db94e6b1a))

### Merged PRs

- Set up Jupyter Releaser [#56](https://github.com/y-crdt/ypy-websocket/pull/56) ([@davidbrochart](https://github.com/davidbrochart))
- include tests in sdist [#55](https://github.com/y-crdt/ypy-websocket/pull/55) ([@bollwyvl](https://github.com/bollwyvl))
- use 127.0.0.1 instead of localhost [#54](https://github.com/y-crdt/ypy-websocket/pull/54) ([@bollwyvl](https://github.com/bollwyvl))
- Add squashed update after deleting document history [#53](https://github.com/y-crdt/ypy-websocket/pull/53) ([@davidbrochart](https://github.com/davidbrochart))
- Implement YStore versioning [#48](https://github.com/y-crdt/ypy-websocket/pull/48) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/y-crdt/ypy-websocket/graphs/contributors?from=2022-11-22&to=2022-11-25&type=c))

[@bollwyvl](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Abollwyvl+updated%3A2022-11-22..2022-11-25&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ay-crdt%2Fypy-websocket+involves%3Adavidbrochart+updated%3A2022-11-22..2022-11-25&type=Issues)

## 0.7.1
