# Architektura Systemu / System Architecture

## PL: Podział odpowiedzialności
1. **Frontend (Cienki Klient):** Odpowiada WYŁĄCZNIE za wyświetlanie stanu gry (`GameState` otrzymanego z serwera) oraz zbieranie intencji gracza (np. "chcę położyć ten klocek tutaj"). Frontend nie weryfikuje reguł fizyki gry.
2. **Backend (Serwer Autorytatywny):** Weryfikuje każdy ruch, przelicza reguły styku narożnikami i bokami, i wysyła zatwierdzony stan do wszystkich podłączonych ekranów.

## EN: Event-Driven UI
The frontend reacts to events incoming via WebSocket from the server, updating the global application state using React state management.