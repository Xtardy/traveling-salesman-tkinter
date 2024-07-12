import tkinter as tk
from tkinter import messagebox
from functools import partial
import random
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class TravelingSalesmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traveling Salesman Problem")

        self.tsp_size_label = tk.Label(root, text="Number of cities:")
        self.tsp_size_label.pack()

        self.tsp_size_entry = tk.Entry(root)
        self.tsp_size_entry.pack()

        self.generate_button = tk.Button(root, text="Generate Cities", command=self.generate_cities)
        self.generate_button.pack()

        self.solve_button = tk.Button(root, text="Solve TSP", command=self.solve_tsp)
        self.solve_button.pack()

        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.pack()

        self.cities = []
        self.solution = []

    def generate_cities(self):
        self.cities.clear()
        self.canvas.delete("all")

        try:
            tsp_size = int(self.tsp_size_entry.get())
            if tsp_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive integer for the number of cities.")
            return

        self.tsp_size = tsp_size
        for _ in range(tsp_size):
            x = random.randint(20, 580)
            y = random.randint(20, 580)
            self.cities.append((x, y))
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='blue')

    def solve_tsp(self):
        if not self.cities:
            messagebox.showerror("Error", "Please generate cities first.")
            return

        args = self.create_args(self.tsp_size)
        self.main(args)

    def create_args(self, tsp_size):
        class Args:
            pass
        args = Args()
        args.tsp_size = tsp_size
        args.tsp_use_random_matrix = False
        args.tsp_random_forbidden_connections = 0
        args.tsp_random_seed = 0
        return args

    def Distance(self, manager, i, j):
        city_i = self.cities[manager.IndexToNode(i)]
        city_j = self.cities[manager.IndexToNode(j)]
        return int(((city_i[0] - city_j[0]) ** 2 + (city_i[1] - city_j[1]) ** 2) ** 0.5)

    def main(self, args):
        if args.tsp_size > 0:
            manager = pywrapcp.RoutingIndexManager(args.tsp_size, 1, 0)
            routing = pywrapcp.RoutingModel(manager)
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

            cost = routing.RegisterTransitCallback(partial(self.Distance, manager))
            routing.SetArcCostEvaluatorOfAllVehicles(cost)

            assignment = routing.Solve()
            if assignment:
                self.solution.clear()
                self.canvas.delete("solution")
                route_number = 0
                node = routing.Start(route_number)
                while not routing.IsEnd(node):
                    self.solution.append(manager.IndexToNode(node))
                    node = assignment.Value(routing.NextVar(node))
                self.solution.append(0)

                self.draw_solution()
            else:
                messagebox.showerror("Error", "No solution found.")
        else:
            messagebox.showerror("Invalid Input", "Please enter a number of cities greater than 0.")

    def draw_solution(self):
        for i in range(len(self.solution) - 1):
            city1 = self.cities[self.solution[i]]
            city2 = self.cities[self.solution[i+1]]
            self.canvas.create_line(city1[0], city1[1], city2[0], city2[1], fill='red', tags="solution")

if __name__ == "__main__":
    root = tk.Tk()
    app = TravelingSalesmanApp(root)
    root.mainloop()
