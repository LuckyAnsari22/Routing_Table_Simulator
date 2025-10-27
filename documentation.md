# Advanced Project Documentation: Interactive Routing Protocol Simulator

## 1. Executive Summary & Project Vision

**Project Title:** Interactive Routing Protocol Simulator

**Vision:** To demystify the foundational principles of intra-domain network routing by providing an interactive, visual, and educational tool. This simulator bridges the gap between theoretical algorithms (Dijkstra's, Bellman-Ford) and their practical application in well-known routing protocols like OSPF and RIP.

**Core Problem Addressed:** The behavior of routing protocols can be abstract and difficult to visualize. This tool makes these concepts tangible by allowing users to build custom networks, observe routing decisions in real-time, and inspect the data structures (routing tables) that drive network traffic.

## 2. In-Depth Feature Analysis

- **Dynamic Topology Workbench:**
    - **Functionality:** Users can create a network graph from scratch. This includes adding nodes (routers) and creating directed, weighted links (edges) between them.
    - **Educational Value:** This reinforces the concept of a network as a graph data structure, where routers are vertices and links are edges. The ability to set weights demonstrates the concept of "cost," a critical metric in routing decisions.

- **Dual-Algorithm Simulation Engine:**
    - **Dijkstra's Algorithm:** Simulates a **Link-State** routing protocol (like OSPF). It calculates the absolute shortest path from a single source to all other nodes.
    - **Bellman-Ford Algorithm:** Simulates a **Distance-Vector** routing protocol (like RIP). It calculates shortest paths based on information shared between immediate neighbors.
    - **Educational Value:** Allows for direct comparison of the two major classes of interior gateway protocols.

- **Real-Time Network Visualization:**
    - **Functionality:** The network topology is rendered interactively. When a simulation is run, the calculated shortest path is highlighted.
    - **Educational Value:** Provides immediate visual feedback, making it easy to confirm the result of the algorithm and understand the path chosen.

- **Comprehensive Routing Table Generation:**
    - **Functionality:** Generates a detailed routing table for any selected router. The table includes columns for Destination, Next Hop, Total Cost, and the Full Path.
    - **Educational Value:** This is the most critical feature for understanding a router's logic. It shows *exactly* how a router would decide to forward a packet for any given destination.

- **Path-Finding Animation:**
    - **Functionality:** Generates a step-by-step GIF animation of the path being constructed from source to destination.
    - **Educational Value:** Visualizes the process of path discovery, reinforcing how the final path is an aggregation of smaller, sequential hops.

- **Data Export Capabilities:**
    - **Functionality:** Allows the export of all routing tables to a CSV file and animations to a GIF.
    - **Educational Value:** Enables offline analysis and inclusion in reports or presentations.

## 3. Deep Dive: Networking Concepts & Algorithms

This section provides the detailed theory that powers the simulator.

### 3.1. The Network as a Graph

The entire simulation is built on the premise that a network can be modeled as a **directed, weighted graph, G = (V, E)**:
- **V (Vertices):** The set of nodes in the graph, representing the routers.
- **E (Edges):** The set of directed links between nodes, representing physical or logical connections.
- **Weight (Cost):** A numerical value assigned to each edge, `w(u, v)`. In the real world, this cost can be an administrative metric or be inversely proportional to link bandwidth (a faster link has a lower cost), or it could represent latency. The goal of a routing algorithm is to find the path with the minimum total cost.

### 3.2. Routing Algorithm Classes: A Comparison

#### Class 1: Link-State (Simulated with Dijkstra's Algorithm)

- **Real-World Protocol:** OSPF (Open Shortest Path First)
- **Core Idea:** "Every router has a map of the entire network."
- **How it Works:**
    1.  **Discovery:** Each router discovers its immediate neighbors and the cost to reach them.
    2.  **Flooding:** Each router broadcasts this information (its "link-state") to *all other routers* in the network. This is done via Link-State Advertisements (LSAs).
    3.  **Map Building:** After the flooding is complete, every router has received the link-state information from every other router. Each router can then construct an identical, complete graph of the network topology.
    4.  **Path Calculation:** With the full map, each router runs Dijkstra's algorithm locally to calculate the shortest path from itself to every other destination. The results are stored in its routing table.
- **Dijkstra's Algorithm Explained:**
    - **Goal:** Find the shortest path from a `source` node to all other nodes in a weighted graph.
    - **Process:** It maintains a set of "unvisited" nodes and a table of the shortest known distances from the source to every other node. Initially, the distance to the source is 0 and all other distances are infinity.
        1.  Start at the `source` node.
        2.  For the current node, consider all of its unvisited neighbors.
        3.  Calculate their tentative distances through the current node. (e.g., `distance to current node` + `cost to neighbor`).
        4.  If a calculated distance is less than the known distance, update the shortest distance for that neighbor.
        5.  After considering all neighbors of the current node, mark the current node as visited.
        6.  Select the unvisited node with the smallest known distance and repeat the process until the destination is reached (or all nodes are visited). It is a "greedy" algorithm because it always chooses the next best immediate step.
- **Pros:**
    - **Fast Convergence:** Since every router has the full map, it can react quickly to topology changes.
    - **Scalability:** Efficient for large, complex networks.
    - **No "Count-to-Infinity" Problem:** This issue (explained below) does not affect link-state protocols.
- **Cons:**
    - **Higher Resource Usage:** Requires more memory (to store the entire topology) and CPU (to run Dijkstra's algorithm).

#### Class 2: Distance-Vector (Simulated with Bellman-Ford Algorithm)

- **Real-World Protocol:** RIP (Routing Information Protocol)
- **Core Idea:** "Each router knows only about its neighbors, and trusts what they say about the rest of the network."
- **How it Works:**
    1.  **Initialization:** Each router knows the cost to its immediate neighbors. For all other destinations, the cost is infinite.
    2.  **Sharing:** Periodically, each router sends its entire routing table to its immediate neighbors. This is the "distance vector."
    3.  **Information Update:** When a router receives a routing table from a neighbor, it updates its own table based on the new information. For a destination `D`, if neighbor `N` offers a path with cost `C`, the router calculates its own cost to `D` as `(cost to reach N) + C`. If this is better than its current path to `D`, it updates its table.
    4.  **Convergence:** This process repeats. Information slowly propagates across the network. Eventually, the tables "converge," meaning no more updates occur, and everyone has the shortest path information.
- **Bellman-Ford Algorithm Explained:**
    - **Goal:** Find the shortest paths from a source node to all other nodes, with the important ability to handle negative edge weights (though not relevant for this specific simulator's configuration).
    - **Process:** It iteratively "relaxes" edges. It repeats a loop `|V| - 1` times (where |V| is the number of vertices). In each iteration, it goes through every edge `(u, v)` in the network and checks if the path through `u` can improve the current known shortest path to `v`. If `distance to u + cost of edge (u,v) < distance to v`, it updates the distance to `v`. This iterative process ensures that by the end, the shortest path information has propagated across the entire network.
- **Pros:**
    - **Simplicity:** Easier to implement and requires less router memory/CPU.
- **Cons:**
    - **Slow Convergence:** A change in a distant part of the network can take a long time to propagate.
    - **The Count-to-Infinity Problem:** A classic failure mode. If a link goes down, routers can get into a loop where they keep advertising a path to each other that no longer exists, incrementing the cost metric to infinity. (Real-world protocols have safeguards like "split horizon" and "poison reverse" to mitigate this).

### 3.3. The Routing Table: A Router's Brain

The routing table is the direct output of the routing algorithms. Its structure is key:
- **Destination:** The target network or host.
- **Next Hop:** The IP address of the *next* router along the path. This is the most crucial piece of information. A router doesn't need to know the full path, only where to send the packet *next*.
- **Cost:** The total metric for the path. Used to compare different potential routes.
- **Path (Simulator-specific):** The simulator shows the full path for educational purposes. A real router would not store this.

## 4. Technical Implementation Details

- **Framework:** **Streamlit** is used as the web application framework. It allows for rapid development of data-centric apps. The script `routing.py` is re-run from top to bottom whenever a user interacts with a UI widget, and Streamlit cleverly handles caching and state management (`st.session_state`) to maintain the network graph between runs.
- **Graph Logic:** **NetworkX** is the core Python library for graph manipulation.
    - `G = nx.DiGraph()`: Creates a directed graph, perfect for modeling network links.
    - `G.add_node()` / `G.add_edge()`: Functions used to build the topology.
    - `nx.dijkstra_path()` / `nx.bellman_ford_path()`: The high-level NetworkX functions that execute the complex routing algorithms with a single call.
- **Visualization:** **PyVis** is used to render the interactive NetworkX graph. It translates the graph object into an HTML/JavaScript visualization that can be displayed in the browser.
- **Data Handling:** **Pandas** is used to structure and display the routing tables in a clean, tabular format using `pd.DataFrame`.

## 5. Potential Questions & Advanced Discussion Topics

- **Q: What does the "cost" of an edge represent in a real network?**
  - **A:** It's an abstract metric. Network administrators can set it manually. Often, it's calculated as an inverse of the link's bandwidth (e.g., Cost = 10^8 / Bandwidth_in_bps). A 1 Gbps link would have a lower cost than a 100 Mbps link. It can also factor in latency, reliability, or monetary cost.

- **Q: Why simulate two different algorithms? What's the key takeaway?**
  - **A:** To demonstrate the fundamental trade-off in routing: **Link-State (Dijkstra/OSPF)** protocols give every router perfect information, leading to better decisions and faster convergence, but at a higher cost of resources. **Distance-Vector (Bellman-Ford/RIP)** protocols are simpler and less resource-intensive but are slower to adapt and can suffer from routing loops.

- **Q: What happens if a link fails? How would the simulator show this?**
  - **A:** You can simulate a link failure by removing an edge from the topology. Upon re-running the simulation, the algorithms will automatically calculate a new shortest path, if one exists. This demonstrates the dynamic, self-healing nature of routing protocols.

- **Q: The simulator's Bellman-Ford doesn't have the "count-to-infinity" problem. Why?**
  - **A:** Because the simulator runs the algorithm on a static graph from a global perspective. In a real network, the problem arises because each router is a distributed agent with incomplete information, sharing updates over time. The simulator calculates the result instantly, so it doesn't model the temporal, distributed nature that leads to this specific issue.

- **Q: How does this project scale? Could it simulate the internet?**
  - **A:** No. This is a simulator for **Interior Gateway Protocols (IGPs)**, which operate *within* a single autonomous system (AS), like a university campus or a corporate network. The internet is a network of *many* different ASs, and it uses an **Exterior Gateway Protocol (EGP)**, primarily **BGP (Border Gateway Protocol)**, which is far more complex and policy-based.
