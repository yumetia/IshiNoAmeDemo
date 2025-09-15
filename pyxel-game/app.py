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
from scenes import draw_start_scene, draw_game_over  # only what we need


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="石の雨")
        pyxel.load("my_resource.pyxres")

        self.current_scene = START_SCENE

        self.score = 0
        self.step_speed = 50
        self.stone_interval = STONE_INTERVAL
        self.stone_speed = STONE_SPEED
        self.is_colliding = False
        self.game_over_timer = 60

        self.player = None
        self.stones = []

        pyxel.run(self.update, self.draw)


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

    # Game loop (PLAY)
    def update_play_scene(self):
        # On collision => game over countdown, then return to start
        if self.is_colliding:
            self.game_over_timer -= 1
            if self.game_over_timer <= 0:
                self.current_scene = START_SCENE
            return

        # Score + difficulty ramp-up
        self.score += 1
        if self.score > self.step_speed:
            self.step_speed += 50
            if self.score < 2800:
                self.stone_speed += 0.1
            elif self.stone_interval > 7:
                self.stone_interval -= 1

        self.player.move()

        if pyxel.frame_count % self.stone_interval == 0:
            self.stones.append(
                Stone(pyxel.rndi(0, SCREEN_WIDTH - 6), 0, self.stone_speed)
            )

        # Updates and collisions
        for stone in self.stones.copy():
            stone.update()

            # Simple AABB collision
            if (
                self.player.x <= stone.x <= self.player.x + 8
                and self.player.y <= stone.y <= self.player.y + 8
            ):
                self.is_colliding = True

            # Remove when off-screen
            if stone.y >= SCREEN_HEIGHT:
                self.stones.remove(stone)

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
            # Dynamic background
            if self.score > 3000:
                pyxel.cls(pyxel.COLOR_GRAY)
            else:
                # PLAY_SCREEN_COLOR is a string (e.g., "pyxel.COLOR_NAVY"), evaluate it
                pyxel.cls(eval(PLAY_SCREEN_COLOR))

            # Score
            pyxel.text(2, 2, f"{self.score}", pyxel.COLOR_RED)

            if self.is_colliding:
                draw_game_over()

            # Draw entities
            for stone in self.stones:
                stone.draw()
            self.player.draw()


if __name__ == "__main__":
    App()
