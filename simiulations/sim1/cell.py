#simiulation 0001 --- First Living Cell:

class Cell:

    def __init__(self):
        self.energy = 100
        self.nutrients = 50
        self.waste = 0
        self.alive = True

    def eat(self, food):
        self.nutrients += food

    def metabolise(self):
        self.nutrients -= 10
        self.energy += 3
        self.waste += 7

    def update(self):
        self.energy -= 10
        if self.energy <= 0:
            self.die()
    def die(self):
        self.alive = False

    def __str__(self):
        return (

            f"Energy: {self.energy}\n"
            f"Nutrients: {self.nutrients}\n"
            f"Waste: {self.waste}\n"
            f"Alive: {self.alive}\n"
            "=========================="
        )