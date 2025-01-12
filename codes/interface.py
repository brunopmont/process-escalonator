import tkinter as tk
import time

m = tk.Tk()

background = tk.Canvas(m, height=480, width=720)
background.pack()

memory = tk.Canvas(m, background='red', height=100, width=300)
memory.pack(side='top')

x1, y1 = 10, 10
x2, y2 = 20, 20

retangulo_vermelho = memory.create_rectangle(x1, y1, x2, y2, fill='red')

for i in range(0, 600, 5):
    memory.coords(retangulo_vermelho, x1, y1, x2 + i, y2)
    memory.update()
    time.sleep(0.01)

m.mainloop()
