import sys, os
import time
import subprocess
import termios, tty

SPLASH_WIDTH = 49
SPLASH_HEIGHT = 12

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    ch = None
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_cols():
    output = subprocess.run(['tput', 'cols'], capture_output=True).stdout
    return int(output)

def get_rows():
    output = subprocess.run(['tput', 'lines'], capture_output=True).stdout
    return int(output)

def show_splash():
    cols = get_cols()
    rows = get_rows()

    start_col = (cols - SPLASH_WIDTH) // 2
    start_row = (rows - SPLASH_HEIGHT) // 2

    f = open('ascii.color', 'r')
    lines = f.readlines()
    f.close()

    print('\033[1;1H', end='', flush=True)
    # Position row.
    for i in range(start_row):
        print('')
    # Draw splash.
    for line in lines:
        print(' ' * start_col, end='')
        print(line, end='')
    print('')


class Color:
    def __init__(self, value):
        self._value = value

    def is_default(self):
        if self._value == -1:
            return True

        return False

    def value(self):
        return self._value


Color.Default = Color(-1)
Color.Black = Color(0)
Color.Red = Color(1)
Color.Green = Color(2)
Color.Yellow = Color(3)
Color.Blue = Color(4)
Color.Magenta = Color(5)
Color.Cyan = Color(6)
Color.White = Color(7)


class View:
    def __init__(self, x, y, width, height):
        self._focused = False
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._bg = Color.Default
        self._fg = Color.Default
        self._selected_bg = Color.Black
        self._selected_fg = Color.Red

    def set_bg(self, color):
        self._bg = color

    def set_fg(self, color):
        self._fg = color

    def begin_bg(self):
        if not self._bg.is_default():
            print(f'\033[48;5;{self._bg.value()}m', end='')

    def begin_fg(self):
        if not self._fg.is_default():
            print(f'\033[38;5;{self._fg.value()}m', end='')

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def update(self):
        row = self._y + 1
        col = self._x + 1

        print(f'\033[{row};{col}H', end='', flush=True)
        print('\033[48;5;196m', end='')
        for i in range(self._height + 1):
            # Move to begin.
            print(f'\033[{row};{col}H', end='', flush=True)
            # Reset colors.
            print('\033[0m', end='', flush=True)
            # Set bg.
            self.begin_bg()
            # Set fg.
            self.begin_fg()

            print('*' * self._width, end='', flush=True)
            # Reset colors.
            print('\033[0m', end='', flush=True)
            row = row + 1


class Eye(View):
    def __init__(self, width):
        height = 5
        super().__init__(0, 0, width, height)

        self.set_bg(Color.Black)
        self.set_fg(Color.Red)

        self._eye_id = ''

    def set_eye_id(self, eye_id):
        self._eye_id = eye_id

    def update(self):
        row = 1
        col = self._x + 1

        print(f'\033[{row};{col}H', end='', flush=True)
        for i in range(self._height + 1):
            # Move to begin.
            print(f'\033[{row};{col}H', end='', flush=True)
            # Reset colors.
            print('\033[0m', end='', flush=True)
            # Set bg.
            self.begin_bg()
            # Set fg.
            self.begin_fg()

            print('+', end='')
            print('-' * self._width - 2, end='')
            print('+', end='')

            # Reset colors.
            print('\033[0m', end='', flush=True)
            row = row + 1

class Shell:
    def __init__(self):
        self._cursor_mode = True
        self._views = []
        self._prompt_input = ''
        self._pwd = ''
        self._return = 0

    def enter(self):
        print('\033[?1049h', end='', flush=True)

    def leave(self):
        print('\033[?1049l', end='')

    def hide_cursor(self):
        print('\033[?25l', end='')

    def show_cursor(self):
        print('\033[?25h', end='')

    def render(self):
        print('\033[1;1H========', end='', flush=True)

        cols = get_cols()
        rows = get_rows()

        for view in self._views:
            view.update()


class CloseButton(Eye):
    def __init__(self):
        self._focused = False

        self.set_eye_id('close-button')


if __name__ == '__main__':
    shell = Shell()
    shell.enter()

    shell.hide_cursor()
    show_splash()
    time.sleep(1)
    shell.show_cursor()

    shell.render()

    view = View(0, 0, 5, 3)
    view.set_x(2)
    view.set_y(2)
    view.set_bg(Color.White)
    view.set_fg(Color.Cyan)
    view.update()

    print()
    print('-- Prompt -', end='')
    print('-' * (get_cols() - 11))
    print('$ ', end='')
    i = input()
    while i.strip(' ') != 'exit':
        print('$ ', end='')
        i = input()

    shell.leave()
