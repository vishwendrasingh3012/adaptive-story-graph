import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from collections import deque
from matplotlib import animation

STORY_FILE = "story_progress.json"

# ------------------ Data Management ------------------
def load_story():
    if not os.path.exists(STORY_FILE):
        return {"current_node": "start", "visited": [], "history": []}
    with open(STORY_FILE, "r") as f:
        return json.load(f)

def save_story(data):
    with open(STORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ Story Graph Definition ------------------
class AdaptiveStoryGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.create_story()

    def create_story(self):
        """Define extended storyline and branches"""
        self.G.add_node("start", text="You wake up in a mysterious forest. What will you do?")
        self.G.add_node("explore", text="You decide to explore the forest. You hear strange noises ahead.")
        self.G.add_node("stay", text="You decide to stay put. The sun starts to set.")
        self.G.add_node("follow_sound", text="You follow the sound and discover a hidden waterfall shimmering in the sunlight.")
        self.G.add_node("run_away", text="You run away and find a small village nearby with friendly faces.")
        self.G.add_node("make_fire", text="You make a fire to stay warm. Suddenly, someone approaches you cautiously...")
        self.G.add_node("sleep", text="You go to sleep and wake up to find food left nearby.")
        self.G.add_node("talk_stranger", text="You talk to the stranger. They claim to be a traveler who lost their group.")
        self.G.add_node("avoid_stranger", text="You avoid the stranger and hide behind a tree, watching them leave silently.")
        self.G.add_node("help_traveler", text="You decide to help the traveler find their camp. They thank you sincerely.")
        self.G.add_node("refuse_help", text="You refuse to help and continue alone, feeling uneasy about your decision.")
        self.G.add_node("explore_village", text="In the village, you meet the elder who warns of a coming storm.")
        self.G.add_node("rest_in_village", text="You rest in a cozy hut. Villagers share stories of the forest spirits.")
        self.G.add_node("climb_waterfall", text="You climb behind the waterfall and find an ancient stone door.")
        self.G.add_node("inspect_door", text="The stone door has glowing runes. Touch them?")
        self.G.add_node("touch_runes", text="You touch the runes — the door opens revealing a hidden temple.")
        self.G.add_node("ignore_runes", text="You decide not to risk it and return to the forest path.")
        self.G.add_node("end_village", text="You reach the village safely. The villagers welcome you as one of their own.")
        self.G.add_node("end_waterfall", text="You discover a treasure behind the waterfall — your courage is rewarded!")
        self.G.add_node("end_mystery", text="The mysterious person helps you find your way home under the moonlight.")
        self.G.add_node("end_temple", text="Inside the temple, you find ancient scrolls that reveal the secret of the forest.")
        self.G.add_node("end_storm", text="You stay in the village through the storm and become part of their community.")
        self.G.add_node("lost_forest", text="You wander too deep into the forest and lose your way... forever.")

        # -------- Story Paths (Edges) --------
        self.G.add_edges_from([
            ("start", "explore"), ("start", "stay"),
            ("explore", "follow_sound"), ("explore", "run_away"),
            ("stay", "make_fire"), ("stay", "sleep"),
            ("follow_sound", "climb_waterfall"),
            ("climb_waterfall", "inspect_door"),
            ("inspect_door", "touch_runes"), ("inspect_door", "ignore_runes"),
            ("ignore_runes", "lost_forest"), ("touch_runes", "end_temple"),
            ("run_away", "explore_village"), ("run_away", "rest_in_village"),
            ("make_fire", "talk_stranger"), ("make_fire", "avoid_stranger"),
            ("talk_stranger", "help_traveler"), ("talk_stranger", "refuse_help"),
            ("help_traveler", "end_mystery"), ("refuse_help", "lost_forest"),
            ("rest_in_village", "end_storm"), ("explore_village", "end_village"),
            ("sleep", "end_mystery"), ("follow_sound", "end_waterfall")
        ])

    def get_choices(self, node):
        return list(self.G.successors(node))

    def get_text(self, node):
        return self.G.nodes[node]["text"]

# ------------------ Hierarchical Layout ------------------
def hierarchy_layout(G, root='start', width=2.0, vert_gap=1.2, vert_loc=0):
    levels = {root: 0}
    queue = deque([root])
    while queue:
        v = queue.popleft()
        for child in G.successors(v):
            if child not in levels:
                levels[child] = levels[v] + 1
                queue.append(child)

    layer_nodes = {}
    for node, level in levels.items():
        layer_nodes.setdefault(level, []).append(node)

    pos = {}
    for depth, nodes in layer_nodes.items():
        dx = width / (len(nodes) + 1)
        for i, node in enumerate(nodes):
            pos[node] = (i * dx, -depth * vert_gap + vert_loc)
    return pos

# ------------------ GUI ------------------
class StoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📖 Adaptive Story Graph (Animated)")
        self.geometry("800x550")
        self.config(bg="#f8f9fa")

        self.story_graph = AdaptiveStoryGraph()
        self.story_data = load_story()
        self.history_stack = self.story_data.get("history", [])

        self.create_ui()
        self.show_story(self.story_data["current_node"])

    def create_ui(self):
        tk.Label(self, text="📚 Adaptive Story Graph", font=("Arial", 22, "bold"), bg="#f8f9fa").pack(pady=10)

        self.story_text = tk.Label(self, text="", wraplength=700, justify="center",
                                   font=("Arial", 14), bg="#ffffff", relief="solid", padx=10, pady=10)
        self.story_text.pack(pady=20)

        self.choice_frame = tk.Frame(self, bg="#f8f9fa")
        self.choice_frame.pack(pady=10)

        btn_frame = tk.Frame(self, bg="#f8f9fa")
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="⬅ Go Back", command=self.go_back).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="🎞 Visualize (Animated)", command=self.show_graph_animated).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="🔁 Restart", command=self.reset_story).grid(row=0, column=2, padx=10)
        ttk.Button(btn_frame, text="Exit", command=self.quit).grid(row=0, column=3, padx=10)

    def show_story(self, node):
        self.story_text.config(text=self.story_graph.get_text(node))
        self.clear_choices()
        choices = self.story_graph.get_choices(node)
        if not choices:
            tk.Label(self.choice_frame, text="🌟 The End 🌟", font=("Arial", 14, "bold"),
                     bg="#f8f9fa", fg="green").pack()
            return
        for choice in choices:
            ttk.Button(self.choice_frame, text=self.story_graph.get_text(choice)[:60] + "...",
                       command=lambda c=choice: self.next_node(c)).pack(pady=5)

    def clear_choices(self):
        for w in self.choice_frame.winfo_children():
            w.destroy()

    def next_node(self, node):
        cur = self.story_data["current_node"]
        self.history_stack.append(cur)
        self.story_data["current_node"] = node
        if node not in self.story_data["visited"]:
            self.story_data["visited"].append(node)
        self.story_data["history"] = self.history_stack
        save_story(self.story_data)
        self.show_story(node)

    def go_back(self):
        if not self.history_stack:
            messagebox.showinfo("Backtracking", "You are already at the beginning!")
            return
        prev = self.history_stack.pop()
        self.story_data["current_node"] = prev
        self.story_data["history"] = self.history_stack
        save_story(self.story_data)
        self.show_story(prev)

    # ------------------ Animated Graph Visualization ------------------
    def show_graph_animated(self):
        G = self.story_graph.G
        pos = hierarchy_layout(G, root='start')
        visited = set(self.story_data["visited"])
        current = self.story_data["current_node"]

        fig, ax = plt.subplots(figsize=(12, 7))
        plt.title("📘 Adaptive Story Graph — Animated (Top-Down)", fontsize=14, fontweight="bold")
        plt.axis("off")

        nodes = list(G.nodes())
        edges = list(G.edges())
        drawn_nodes, drawn_edges = [], []

        def update(frame):
            ax.clear()
            plt.axis("off")
            plt.title("📘 Story Graph Progress", fontsize=14, fontweight="bold")

            step_nodes = nodes[:min(len(nodes), frame + 1)]
            step_edges = [e for e in edges if e[0] in step_nodes and e[1] in step_nodes]

            colors = []
            for n in step_nodes:
                if n == current:
                    colors.append("#7EB6FF")
                elif n in visited:
                    colors.append("#A8E6CF")
                else:
                    colors.append("#FFF9C4")

            nx.draw(G.subgraph(step_nodes), pos, with_labels=True,
                    node_color=colors, node_size=2200, font_size=8,
                    font_weight="bold", edgecolors="black",
                    arrows=True, arrowsize=12, ax=ax)

        ani = animation.FuncAnimation(fig, update, frames=len(nodes), interval=500, repeat=False)
        plt.show()

    def reset_story(self):
        if os.path.exists(STORY_FILE):
            os.remove(STORY_FILE)
        self.story_data = {"current_node": "start", "visited": [], "history": []}
        self.history_stack = []
        save_story(self.story_data)
        self.show_story("start")
        messagebox.showinfo("Restarted", "Story restarted successfully!")

# ------------------ Run ------------------
if __name__ == "__main__":
    app = StoryApp()
    app.mainloop()
