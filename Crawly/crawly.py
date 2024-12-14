import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time as t
from collections import deque


class Crawly:
    _methods = ["bfs", "BFS", "dfs", "DFS"]

    def __init__(self, start_url, search_method, max_time, max_depth):
        self.start_url = start_url
        self.search_method = search_method.upper()
        self.max_time = max_time
        self.max_depth = max_depth
        self.visited = set()
        self.results = []
        self.start_time = t.time()

    def start(self):
        print(
            f"URL '{self.start_url}'\nMethod '{self.search_method}'\nMax Time: {self.max_time}\nMax Depth: {self.max_depth}"
        )
        match self.search_method:
            case "BFS":
                self._bfs()
            case "DFS":
                self._dfs(self.start_url, 0)
        self._save_to_csv()

    def _bfs(self):
        queue = deque([(self.start_url, 0)])
        while queue:
            url, depth = queue.popleft()
            time = t.time() - self.start_time
            if self._should_stop(depth, time):
                continue
            print(f"BFS| {url} | Time: {time} | Depth: {depth}")
            self._process_page(url, depth, queue)

    def _dfs(self, url, depth):
        time = t.time() - self.start_time
        if self._should_stop(depth, time):
            return
        print(f"DFS| {url} | Time: {time} | Depth: {depth}")
        queue = []
        self._process_page(url, depth, queue)
        for link, new_depth in queue:
            if link not in self.visited:
                self._dfs(link, new_depth)

    def _should_stop(self, depth, time):
        return depth > self.max_depth or time > self.max_time

    def _process_page(self, url, depth, queue):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            self.results.append((url, soup.get_text(separator=" ", strip=True)))
            self.visited.add(url)
            # Getting the links
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"])
                if full_url not in self.visited and full_url.startswith("http"):
                    if self.search_method == "BFS":
                        queue.append((full_url, depth + 1))
                    elif self.search_method == "DFS":
                        queue.append((full_url, depth + 1))
        except Exception as e:
            print(f"{url}: {e}")

    def _save_to_csv(self):
        with open(
            f"{self.start_time}.csv", "w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL", "Content"])
            for url, text in self.results:
                writer.writerow([url, text])

    @classmethod
    def methods(self):
        return self._methods
