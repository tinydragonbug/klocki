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