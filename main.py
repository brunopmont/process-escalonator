import tkinter as tk

from memorybar import *

WIDTH, HEIGHT = 720, 480
MEMSIZE = 32768
x_bar = 100
y_bar = 80
master = tk.Tk()
canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT)
canvas.pack()




bar = memorybar(canvas, x_bar, y_bar, WIDTH - 200, MEMSIZE)

v = int(input('1: adicionar processo; 2: remover processo, 0: sair.'))
while v != 0:
    if v == 1:
        mem = int(input("memoria (MB):"))
        id = int(input("id:"))
        bar.add_process(mem, id)
    if v == 2:
        id = int(input("id:"))
        bar.remove_process(id)
    v = int(input('1: adicionar processo; 2: remover processo, 0: sair.'))



master.mainloop()