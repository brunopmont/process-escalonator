from random import *

def randomcolor():
    main = randint(0, 2)
    b_strength = randint(0, 15)
    c_strength = 15 - b_strength
    if b_strength > 9:
        b_strength = chr(b_strength + 97 - 10)
    if c_strength > 9:
        c_strength = chr(c_strength + 97 - 10)
    color = [0, 0, 0, 0, 0, 0]
    color[main * 2] = "f"
    color [main * 2 + 1] = "f"
    color[main * 2 - 1] = str(b_strength)
    color[main * 2 - 2] = str(b_strength)
    color[main * 2 - 3] = str(c_strength)
    color[main * 2 - 4] = str(c_strength)
    end ="#" + "".join(color)
    print(end)
    return end
    

randomcolor()

class memorybar:
    def __init__(self, canvas, x, y, len, memsize):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.len = len
        self.memsize = memsize
        self.colors = ['red', 'orange', 'yellow', 'cyan', 'green', 'blue', 'purple']

        self.emptybar = canvas.create_rectangle(x, y, x + len, y + 40, fill='gray')

        self.processes = []

        self.index = 0
        self.totallen = 0
    
    def add_process(self, size_mb, id):
        size = size_mb/32768 * self.len #conversão de MB para tamanho da barra
        self.processes.append(processbar(self.canvas, self.x, self.y, randomcolor(), id, self.totallen, size))
        self.index += 1
        self.totallen += size


    def remove_process(self, id):
        for i in self.processes:
            if i.id == id:
                i.remove()
                self.totallen -= i.len
                self.index -=1
                offset = i.len
                for j in self.processes:
                    if(self.processes.index(j) > self.processes.index(i)):
                        j.changepos(j.pos - offset)
                self.processes.remove(i)

            

class processbar:
    def __init__(self, canvas, x, y, color, id, pos, len):
        self.x = x
        self.y = y
        self.color = color
        self.id = id
        self.pos = pos
        self.len = len
        self.canvas = canvas
        self.bar = canvas.create_rectangle(self.x + self.pos, self.y, self.x + self.pos + self.len, self.y + 40, fill=color)
    
    def changepos(self, newpos):
        self.pos = newpos
        self.canvas.delete(self.bar)
        self.bar = self.canvas.create_rectangle(self.x + self.pos, self.y, self.x + self.pos + self.len, self.y + 40, fill=self.color)

    def remove(self):
        self.canvas.delete(self.bar)