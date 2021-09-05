# tetris.py

Tetris implemented in pygame using bitboards 


## TODO

### Game Logic
- [x] Clearing of lines
    - [x] Identify tiles that should be removed
    - [x] Drop tiles by the number of removed lines
    - [x] Render effect of clearing lines
    - [x] Render effect of dropping tiles
    - [x] BUG: Clearing more than 1 line results in negative shift count bug

- [] Game UI
    - [x] Center main game in middle of screen
    - [] Add next piece UI
    - [] Add stashed piece UI
    - [] Add score counter

- [] Scoring
    - [] Implement scoring mechanism based on lines cleard
    - [] Render scores
    - [] (?) scoreboard

- [] Piece stash
    - [] Allow player to stash the existing piece and call the next piece if stash is empty
    - [] Allow player to swap the current piece with stashed piece
