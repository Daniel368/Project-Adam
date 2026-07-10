from cell import Cell

cell = Cell()

print(      "==========================\n"
            "      PROJECT ADAM\n"
            "Simulation 0001\n"
            "==========================")

while cell.alive:
    cell.eat(100)
    cell.metabolise()
    cell.update()

    print(cell)


print("The cell has died")
