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