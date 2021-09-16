# tetris.py

Tetris implemented in pygame using bitboards 

## Why build a game with python and pygame?
I've tried dabbling with both Godot and Unity, but have never progressed very far with either frameworks. When I stumbled upon [DaFluffyPotato's channel](https://www.youtube.com/c/DaFluffyPotato), I was convinced that doing pygame was definitely a viable option. Given that I work with python during my day job, this was the natural choice to try getting started in game dev again.

## Why use bitboards?
I experienced several issues with using collisions to determine if a particular action can be allow; If the current tetrimino is colliding at the bottom, we should lock said tetrimino and generate a new one. What I learnt quickly is that Rects need to be overlapping before it is considered a collision, and my naive solution led to tetriminos getting locked when they are touching at the corners. On hindside, I could have easily adjusted the Rects in the relevant direction when I needed to do collision checks, but my pea brain couldn't figure this out.

Instead, I went back to bitboards, which I've used previously when trying to build a chess game. A bitboard is essentially a binary number where 1's indicate where a particular cell is occupied. A J block can essentially be represented as
```
001
111
```

What this allows me to do is I can have a number that represents the state of the board, and shift the active piece around the board to check for collisions. Once all the checks are completed, I can then translate the binary number into a set of coordinates for rendering.

---

## TODO

### Game Logic
- [x] Clearing of lines
    - [x] Identify tiles that should be removed
    - [x] Drop tiles by the number of removed lines
    - [x] Render effect of clearing lines
    - [x] Render effect of dropping tiles
    - [x] BUG: Clearing more than 1 line results in negative shift count bug

- [ ] Game UI
    - [x] Center main game in middle of screen
    - [x] Add next piece UI
    - [x] Add stashed piece UI
    - [ ] Add score counter

- [ ] Scoring
    - [ ] Implement scoring mechanism based on lines cleared
    - [ ] Render scores
    - [ ] (?) scoreboard

- [x] Piece stash
    - [x] Allow player to stash the existing piece and call the next piece if stash is empty
    - [x] Allow player to swap the current piece with stashed piece

- [ ] Scenes
    - [ ] Add main menu screen
    - [ ] Add pause screen
    - [ ] (?) Add high score screen

- [ ] Polish
    - [ ] Add fancy background with falling tetriminos
    - [ ] Having fancy falling tetriminos respond to user input

## Credits
- L-Gad [Tetriminos Pack](https://l-gad.itch.io/tetriminos-asset-pack)
