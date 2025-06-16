# 🌐 Routing Protocol Simulator with Animation

An interactive Streamlit web app to simulate and visualize computer network routing using **Dijkstra (OSPF)** and **Bellman-Ford (RIP)** algorithms. Users can build their own topologies, view path animations, generate routing tables, and export data.

![Routing Animation](example_gif.gif)

---

## Features

- **Add/Remove Nodes and Edges** interactively
- **Visualize topology** using PyVis
- Simulate **Dijkstra (OSPF)** or **Bellman-Ford (RIP)**
- Show **routing table per router**
- Export:
  - Routing tables as **CSV**
  - Routing path animation as **GIF**

---

## What is Routing?

Routing is the process of selecting paths in a network along which to send data packets. Protocols like OSPF and RIP help determine the best path based on metrics like cost or hop count.

### Supported Routing Protocols:
- **Dijkstra (OSPF):** Uses link cost and calculates shortest path tree from source.
- **Bellman-Ford (RIP):** Based on hop count, allows negative weights (with care), and works well in distance-vector models.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/routing-simulator.git
cd routing-simulator
