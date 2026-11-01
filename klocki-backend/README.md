# Klocki — Multiplayer Strategy Game

**PL:** Klocki to wieloosobowa gra logiczno-strategiczna oparta na architekturze klient-serwer. Projekt wykorzystuje podejście Polyrepo, oddzielając logikę silnika gry i serwera (Python/FastAPI) od interfejsu użytkownika (React/TypeScript).
**EN:** Klocki is a client-server multiplayer logic and strategy game. The project uses a Polyrepo approach, separating the game engine and server logic (Python/FastAPI) from the user interface (React/TypeScript).

## Repozytoria / Repositories
*   **Backend:** `[Link to klocki-backend]` (FastAPI, WebSockets, Game Engine)
*   **Frontend:** `[Link to klocki-frontend]` (React, TypeScript, Mobile/TV UI)

## Stos Technologiczny / Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.12+, FastAPI | Serwer autorytatywny, silnik gry, walidacja / Authoritative server, game engine, validation |
| **Frontend** | React, TypeScript, Vite | Interfejs dla dużych ekranów i kontrolerów / UI for large screens and controllers |
| **Network** | WebSockets (WSS) | Dwukierunkowa komunikacja w czasie rzeczywistym / Real-time bidirectional communication |

## Uruchomienie lokalne / Local Development

### PL: Wymagania
*   Zainstalowany Docker i Docker Compose.
*   Node.js (dla lokalnego rozwoju frontendu) oraz Python 3.12+ (dla backendu).

### EN: Requirements
*   Docker and Docker Compose installed.
*   Node.js (for local frontend development) and Python 3.12+ (for backend).

### PL: Szybki start (Docker) / EN: Quick Start (Docker)
1. **Backend:** `cd klocki-backend && docker-compose up --build`
2. **Frontend:** `cd klocki-frontend && docker-compose up --build`