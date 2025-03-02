import random
import time as t
import csv
from datetime import datetime

import networkx as nx
import plotly.graph_objects as go
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright


class Crawly:
    _methods = ["BFS", "DFS"]

    def __init__(
        self,
        start_url,
        search_method,
        max_time,
        max_depth,
        full_graph,
        proxy_server,
        proxy_username,
        proxy_password,
    ):
        self._start_url = start_url
        self._search_method = search_method.upper()
        self._max_time = max_time
        self._max_depth = max_depth
        self._full_graph = full_graph
        self._proxy_server = proxy_server
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password
        self._user_agent = UserAgent().random
        self._prev_url = "https://www.google.com/"
        self._start_time = t.time()
        self._visited = set()
        self._results = []
        self._edges = []

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
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                slow_mo=random.uniform(0, 2) * 1000,
                timeout=20000,
                proxy=(
                    {
                        "server": self._proxy_server,
                        "username": self._proxy_username,
                        "password": self._proxy_password,
                    }
                    if self._proxy_server
                    else None
                ),
            )
            page = browser.new_page()
            match self._search_method:
                case "BFS":
                    self._bfs(page)
                case "DFS":
                    self._dfs(page, self._start_url, 0)
            browser.close()
        self._save()

    def _bfs(self, page):
        queue = deque([(self._start_url, 0)])
        while queue:
            url, depth = queue.popleft()
            time = t.time() - self._start_time + 1
            if self._should_stop(depth, time):
                return
            print(f"{self._time(time)} | {depth}")
            try:
                self._process_page(page, url, depth, queue)
            except Exception as e:
                raise RuntimeError(
                    f"UNRESOLVED EXCEPTION OCCURED ... Check Internet Connection or Proxy Server.\nInfo:\n{e}"
                )

    def _dfs(self, page, url, depth):
        time = t.time() - self._start_time + 1
        if self._should_stop(depth, time):
            return
        print(f"{self._time(time)} | {depth}")
        queue = []
        try:
            self._process_page(page, url, depth, queue)
        except Exception as e:
            raise RuntimeError(
                f"UNRESOLVED EXCEPTION OCCURED ... Check Internet Connection or Proxy Server.\nInfo:\n{e}"
            )
        for link, new_depth in queue:
            if link not in self._visited:
                self._dfs(page, link, new_depth)

    def _should_stop(self, depth, time):
        return depth > self._max_depth or time > self._max_time

    def _process_page(self, page, url, depth, queue):
        soup = None
        try:
            soup = self._process_page_soap(page, url)
        except Exception:
            soup = self._process_page_soap(page, url, False)

        self._results.append((url, soup.get_text(separator=" ", strip=True)))
        self._visited.add(url)
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(url, a_tag["href"])
            parsed_url = urlparse(full_url)
            if full_url not in self._visited and full_url.startswith("http"):
                if not parsed_url.path.endswith(
                    (".jpg", ".png", ".css", ".js", ".svg")
                ):
                    self._edges.append((url, full_url))
                    queue.append((full_url, depth + 1))

    def _process_page_soap(self, page, url, not_protected=True):
        headers = {
            "User-Agent": self._user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "pl-PL,pl;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
            "Referer": self._prev_url,
        }
        page.set_extra_http_headers(headers)
        self._prev_url = url

        page.goto(url)

        if not not_protected:
            try:
                cookie_button = page.wait_for_selector(
                    "button[data-role='accept-consent']",
                    timeout=(random.uniform(1, 4) * 1000),
                )
                cookie_button.click()
            except Exception:
                pass

        body_content = page.content()
        soup = BeautifulSoup(body_content, "html.parser")

        # CAPTCHA
        if not not_protected and self._is_captcha_page(soup, body_content):
            print("CAPTCHA detected. Waiting for user to resolve it...")
            try:
                with page.expect_navigation(timeout=120000):
                    input("Press Enter after solving CAPTCHA...")
            except Exception:
                pass
            body_content = page.content()
            soup = BeautifulSoup(body_content, "html.parser")

        return soup

    def _is_captcha_page(self, soup, body_content):
        keywords = ["captcha", "recaptcha", "verify"]

        if any(keyword in body_content.lower() for keyword in keywords):
            return True

        for img in soup.find_all("img"):
            if (
                "captcha" in img.get("src", "").lower()
                or "captcha" in img.get("alt", "").lower()
            ):
                return True

        return False

    def _time(self, time):
        hours, remainder = divmod(int(time), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _save(self):
        filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self._save_to_csv(filename)
        if len(self._edges) > 1:
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
