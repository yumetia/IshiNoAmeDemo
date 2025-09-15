# app.py
import pyxel  # type: ignore

from settings import (
    STONE_INTERVAL,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    START_SCENE,
    PLAY_SCENE,
    STONE_SPEED,
    PLAY_SCREEN_COLOR,
)
from stone import Stone
from player import Player
from scenes import draw_start_scene, draw_game_over  # uniquement ce dont on a besoin


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="石の雨")
        pyxel.load("my_resource.pyxres")

        # Scène courante : on démarre sur l'écran de start
        self.current_scene = START_SCENE

        # État du jeu
        self.score = 0
        self.step_speed = 50
        self.stone_interval = STONE_INTERVAL
        self.stone_speed = STONE_SPEED
        self.is_colliding = False
        self.game_over_timer = 60

        # Entités
        self.player = None
        self.stones = []

        pyxel.run(self.update, self.draw)

    # -----------------------
    # Scènes / transitions
    # -----------------------
    def reset_play_scene(self):
        self.score = 0
        self.is_colliding = False
        self.game_over_timer = 60
        self.step_speed = 50
        self.stone_speed = STONE_SPEED
        self.stone_interval = STONE_INTERVAL
        self.player = Player()
        self.stones = []
        self.current_scene = PLAY_SCENE

    def update_start_scene(self):
        if (
            pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.KEY_SPACE)
        ):
            self.reset_play_scene()

    # -----------------------
    # Boucle de jeu (PLAY)
    # -----------------------
    def update_play_scene(self):
        # Si collision => phase de game over avec timer, puis retour start
        if self.is_colliding:
            self.game_over_timer -= 1
            if self.game_over_timer <= 0:
                self.current_scene = START_SCENE
            return

        # Score + ramp-up
        self.score += 1
        if self.score > self.step_speed:
            self.step_speed += 50
            if self.score < 2800:
                self.stone_speed += 0.1
            elif self.stone_interval > 7:
                self.stone_interval -= 1

        # Déplacements / spawns
        self.player.move()

        if pyxel.frame_count % self.stone_interval == 0:
            self.stones.append(
                Stone(pyxel.rndi(0, SCREEN_WIDTH - 6), 0, self.stone_speed)
            )

        # Mises à jour et collisions
        for stone in self.stones.copy():
            stone.update()

            # Collision AABB très simple
            if (
                self.player.x <= stone.x <= self.player.x + 8
                and self.player.y <= stone.y <= self.player.y + 8
            ):
                self.is_colliding = True

            # Nettoyage si sortie d'écran
            if stone.y >= SCREEN_HEIGHT:
                self.stones.remove(stone)

    # -----------------------
    # Cycle Pyxel
    # -----------------------
    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()

    def draw(self):
        if self.current_scene == START_SCENE:
            draw_start_scene()

        elif self.current_scene == PLAY_SCENE:
            # Fond dynamique
            if self.score > 3000:
                pyxel.cls(pyxel.COLOR_GRAY)
            else:
                # PLAY_SCREEN_COLOR est une chaîne (ex: "pyxel.COLOR_NAVY"), on l'évalue
                pyxel.cls(eval(PLAY_SCREEN_COLOR))

            # Score
            pyxel.text(2, 2, f"{self.score}", pyxel.COLOR_RED)

            # Game over overlay si collision
            if self.is_colliding:
                draw_game_over()

            # Dessins
            for stone in self.stones:
                stone.draw()
            self.player.draw()


if __name__ == "__main__":
    App()
