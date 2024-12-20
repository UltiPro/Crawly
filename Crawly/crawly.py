import requests
import time as t
import csv
import networkx as nx
import plotly.graph_objects as go

from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime


class Crawly:
    _methods = ["BFS", "DFS"]

    def __init__(self, start_url, search_method, max_time, max_depth, full_graph):
        self._start_url = start_url
        self._search_method = search_method.upper()
        self._max_time = max_time
        self._max_depth = max_depth
        self._full_graph = full_graph
        self._visited = set()
        self._results = []
        self._edges = []
        self._start_time = t.time()

    def start(self):
        print(
            f"\nMethod     | {self._search_method}\n"
            + f"Max Time   | {self._max_time} seconds\n"
            + f"Max Depth  | {self._max_depth}\n"
            + f"Start URL  | {self._start_url}\n"
            + f"Full Graph | {self._full_graph}\n"
        )
        print("HH:MM:SS | Depth")
        print("---------|------")
        match self._search_method:
            case "BFS":
                self._bfs()
            case "DFS":
                self._dfs(self._start_url, 0)
        self._save()

    def _bfs(self):
        queue = deque([(self._start_url, 0)])
        while queue:
            url, depth = queue.popleft()
            time = t.time() - self._start_time + 1
            if self._should_stop(depth, time):
                continue
            print(f"{self._time(time)} | {depth}")
            self._process_page(url, depth, queue)

    def _dfs(self, url, depth):
        time = t.time() - self._start_time + 1
        if self._should_stop(depth, time):
            return
        print(f"{self._time(time)} | {depth}")
        queue = []
        self._process_page(url, depth, queue)
        for link, new_depth in queue:
            if link not in self._visited:
                self._dfs(link, new_depth)

    def _should_stop(self, depth, time):
        return depth > self._max_depth or time > self._max_time

    def _process_page(self, url, depth, queue):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            self._results.append((url, soup.get_text(separator=" ", strip=True)))
            self._visited.add(url)
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"])
                if full_url not in self._visited and full_url.startswith("http"):
                    self._edges.append((url, full_url))
                    queue.append((full_url, depth + 1))
        except Exception as e:
            print(f"Unresolved exception during processing '{url}': {e}")

    def _time(self, time):
        hours, remainder = divmod(int(time), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _save(self):
        filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self._save_to_csv(filename)
        self._save_graph(filename)
        print(f"\nResults saved to '{filename}'.csv/html at current directory.")

    def _save_to_csv(self, filename):
        with open(filename + ".csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL", "Content"])
            for url, text in self._results:
                writer.writerow([url, text])

    def _save_graph(self, filename):
        graph = nx.DiGraph()
        graph.add_edges_from(
            self._edges
            if self._full_graph
            else [
                (src, dst)
                for src, dst in self._edges
                if src in self._visited and dst in self._visited
            ]
        )

        pos = nx.spring_layout(graph)
        edge_x = []
        edge_y = []

        # Drawing edges
        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        # Drawing nodes
        node_x, node_y = zip(*pos.values())
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=list(graph.nodes()),
            textposition="top center",
            marker=dict(
                size=10, color="lightblue", line=dict(width=2, color="DarkSlateGrey")
            ),
        )

        # Interactive Visualization
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                title=f"Interactive Visualization of {filename}",
                margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False),
            ),
        )
        fig.write_html(filename + ".html")

    @classmethod
    def methods(self):
        return self._methods
