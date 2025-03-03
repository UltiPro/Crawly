# Crawly
Crawly created by Patryk 'UltiPro' Wójtowicz using Python.

The project is a web crawler that implements both BFS and DFS search methods. It can be configured by selecting options such as search method, time limits, search depth, whether to generate a full graph, and optional proxy server settings. The application collects only URLs and the contents of "a" tags. However, the code can be easily adapted to specific needs in the "_process_page" function. During execution, the program launches a browser using the Playwright package. The browser navigates through web pages, if necessary, it pauses to let the user solve captchas etc. The output consists of a CSV file containing URLs and "a" tags contents, as well as an HTML page with a graph representing the connections between websites.

# Dependencies and Usage

Dependencies:

<ul>
    <li>beautifulsoup4 4.13.3</li>
    <li>bs4 0.0.2</li>
    <li>fake-useragent 2.0.3</li>
    <li>greenlet 3.1.1</li>
    <li>narwhals 1.28.0</li>
    <li>networkx 3.4.2</li>
    <li>numpy 2.2.3</li>
    <li>packaging 24.2</li>
    <li>playwright 1.50.0</li>
    <li>plotly 6.0.0</li>
    <li>pyee 12.1.1</li>
    <li>soupsieve 2.6</li>
    <li>typing_extensions 4.12.2</li>
</ul>

Installation:

> cd "/Crawly"

> pip install -r requirements.txt

> playwright install

### Using the app

> python main.py [url-address] [options]

| Option           | Short | Description             | Default Value |
| ---------------- | ----- | ----------------------- | ------------- |
| --method         | -m    | Search method           | bfs           |
| --time           | -t    | Execution time (s)      | 60            |
| --depth          | -d    | Maximum search depth    | 10            |
| --full_graph     | -fg   | Generate a full graph   | False         |
| --proxy_server   | -ps   | Proxy server IP/address | —             |
| --proxy_username | -pu   | Proxy username          | —             |
| --proxy_password | -pp   | Proxy password          | —             |

# Preview

![Terminal Preview](/screenshots/terminal.png)

![CSV Preview](/screenshots/csv.png)

![HTML Preview](/screenshots/html.png)
