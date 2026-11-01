klocki-backend/
├── app/
│   ├── api/             # HTTP endpoints (FastAPI)
│   ├── core/            # Config, security, exceptions
│   ├── game/            # Game logic, board state, move validation (Python pure logic)
│   ├── ws/              # WebSocket managers and event handlers
│   └── main.py          # Application entry point
├── tests/               # Pytest (unit, integration, AI tests)
├── docs/                # Architecture, Specification, Roadmap
├── .gitignore
├── docker-compose.yml   # DB (if added later) and Backend service
├── Dockerfile
├── requirements.txt     # or pyproject.toml (Poetry)
└── README.md


klocki-frontend/
├── src/
│   ├── components/      # UI components (React)
│   ├── hooks/           # Custom hooks (e.g., useWebSocket, useGameState)
│   ├── store/           # Global state management
│   ├── types/           # TypeScript interfaces (matching backend models)
│   ├── utils/           # Helpers, board coordinate transformers
│   └── App.tsx
├── tests/               # Vitest / React Testing Library
├── docs/                # Architecture, Specification, Roadmap
├── .gitignore
├── docker-compose.yml   # Frontend service for local dev
├── Dockerfile
├── package.json
└── README.md


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

# Architektura Systemu / System Architecture

## PL: Założenia Główne
1. **Serwer Autorytatywny (Authoritative Server):** Serwer (Backend) jest jedynym źródłem prawdy (Single Source of Truth). Frontend odpowiada wyłącznie za renderowanie stanu i wysyłanie intencji gracza (propozycji ruchu).
2. **Polyrepo:** Rozdzielenie kodu na dwa repozytoria. Ułatwia to niezależne wdrażanie i wymusza projektowanie ścisłych kontraktów dla WebSockets.
3. **Event-Driven UI:** Frontend reaguje na zdarzenia przychodzące przez WebSocket z serwera, aktualizując globalny stan aplikacji.

## EN: Core Principles
1. **Authoritative Server:** The server (Backend) is the Single Source of Truth. The frontend is strictly responsible for rendering state and sending player intentions (move proposals).
2. **Polyrepo:** Code is separated into two repositories. This facilitates independent deployment and enforces strict WebSocket contract design.
3. **Event-Driven UI:** The frontend reacts to events incoming via WebSocket from the server, updating the global application state.

## PL: Model Komunikacji (WebSockets) / EN: Communication Model (WebSockets)

| Typ / Type | Kierunek / Direction | Opis / Description |
| :--- | :--- | :--- |
| `ROOM_CREATE` | Client -> Server | Inicjalizacja nowego pokoju gry / Initializes a new game room. |
| `JOIN_ROOM` | Client -> Server | Gracz dołącza za pomocą kodu / Player joins using a code. |
| `GAME_STATE` | Server -> Client | Pełny lub przyrostowy zrzut stanu planszy i tury / Full or delta dump of board and turn state. |
| `MOVE_PROPOSAL` | Client -> Server | Gracz wysyła współrzędne i ID klocka / Player sends coordinates and piece ID. |
| `MOVE_RESULT` | Server -> Client | Akceptacja lub odrzucenie z kodem błędu / Acceptance or rejection with error code. |

## PL: Niezależność Silnika Gry / EN: Game Engine Independence
PL: Logika gry (weryfikacja kolizji, rotacje macierzy klocków) znajduje się w niezależnym module backendu (`app/game`), bez bezpośrednich zależności od FastAPI. Umożliwia to testowanie reguł w izolacji.
EN: Game logic (collision verification, piece matrix rotations) resides in an independent backend module (`app/game`), with no direct dependencies on FastAPI. This allows rules to be tested in complete isolation.


# Plan Rozwoju / Development Roadmap

## Etap 1: Silnik Gry i Testy / Stage 1: Game Engine & Tests
**PL:** Zdefiniowanie wszystkich kształtów (21 klocków, 89 pól), implementacja silnika gry (Python) i testów reguł (kolizje, styk narożnikami). Brak sieci i UI.
**EN:** Define all shapes (21 pieces, 89 squares), implement the game engine (Python), and rule tests (collisions, corner contact). No networking or UI.

## Etap 2: Główne UI i Renderowanie / Stage 2: Main UI & Rendering
**PL:** Przygotowanie interfejsu planszy (React) na duży ekran. Wizualizacja siatki 20x20 i mechanizm upuszczania/rysowania klocków na podstawie mockowanych danych.
**EN:** Build the large-screen board interface (React). Visualize the 20x20 grid and the drop/draw mechanism for pieces using mocked data.

## Etap 3: Pokoje i WebSockets / Stage 3: Rooms & WebSockets
**PL:** Integracja Backend + Frontend. Tworzenie pokojów (FastAPI), generowanie kodów, dołączanie klientów, synchronizacja stanu gry w czasie rzeczywistym.
**EN:** Backend + Frontend integration. Room creation (FastAPI), code generation, client joining, real-time game state synchronization.

## Etap 4: Kontrolery Mobilne / Stage 4: Mobile Controllers
**PL:** Opracowanie widoku kontrolera na smartfony (PWA/Responsive Web). Obsługa gestów dotykowych, obracanie/odbijanie klocków (lokalnie na UI) i wysyłanie `MOVE_PROPOSAL`.
**EN:** Develop the smartphone controller view (PWA/Responsive Web). Touch gesture support, piece rotation/reflection (local to UI), and emitting `MOVE_PROPOSAL`.

## Etap 5: Sztuczna Inteligencja (AI) / Stage 5: Artificial Intelligence
**PL:** Dodanie komputerowego przeciwnika działającego po stronie serwera. Wdrożenie poziomów trudności (Losowy, Średni, Trudny).
**EN:** Add server-side computer opponents. Implement difficulty levels (Random, Medium, Hard).

## Etap 6: Produkcja i Polerowanie / Stage 6: Production & Polish
**PL:** Testy pełnych partii, obsługa rozłączeń (reconnect z nową wersją stanu), animacje UI, wdrożenie do chmury (np. AWS/Render/Vercel).
**EN:** Full-match testing, disconnection handling (reconnect with new state revision), UI animations, cloud deployment (e.g., AWS/Render/Vercel).


# Klocki — Specyfikacja Projektu / Project Specification

## 1. Opis projektu / Project Description
**PL:** Klocki to wieloosobowa gra logiczno-strategiczna polegająca na układaniu różnokształtnych elementów na wspólnej planszy...
**EN:** Klocki is a multiplayer logic and strategy game in which players place differently shaped pieces on a shared board...

## 2. Podstawowe parametry gry / Core Game Specifications
| Parametr / Parameter | Wartość / Value |
| :--- | :--- |
| Nazwa / Name | Klocki |
| Plansza / Board | 20 × 20 pól / squares |
| Liczba graczy / Players | 4 |
| Tryb / Mode | Turowy / Turn-based |
| Sterowanie / Controls | Smartfony / Smartphones |

## 3. Zestaw klocków / Piece Set
| Rodzaj klocka / Piece type | Liczba klocków / Number | Pola na klocek / Squares per piece | Łączna liczba pól / Total squares |
| :--- | :--- | :--- | :--- |
| Pięciopolowe / Pentominoes | 12 | 5 | 60 |
| Czteropolowe / Tetrominoes | 5 | 4 | 20 |
| Trzypolowe / Trominoes | 2 | 3 | 6 |
| Dwupolowe / Dominoes | 1 | 2 | 2 |
| Jednopolowe / Monomino | 1 | 1 | 1 |
| **Razem / Total** | **21** | **—** | **89** |

*(Tutaj wklej resztę punktów od 4 do 16 z zachowaniem formatowania nagłówków `##` oraz pogrubień dla prefixów **PL:** i **EN:**)*


