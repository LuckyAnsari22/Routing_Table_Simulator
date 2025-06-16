import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import matplotlib.pyplot as plt
import imageio.v2 as imageio

# Set page configuration
st.set_page_config(page_title="Routing Simulator with Animation", layout="wide")
st.title("🌐 Interactive Routing Protocol Simulator")

# Initialize session state graph
if 'G' not in st.session_state:
    st.session_state.G = nx.DiGraph()
G = st.session_state.G

# --- Functions ---
def add_node_ui():
    with st.sidebar.expander("➕ Add Node"):
        new_node = st.text_input("Node name")
        if st.button("Add Node"):
            if new_node:
                if new_node in G.nodes:
                    st.warning("Node already exists.")
                else:
                    G.add_node(new_node)
                    st.success(f"Node '{new_node}' added.")

def add_edge_ui():
    with st.sidebar.expander("➕ Add Edge"):
        node1 = st.text_input("From")
        node2 = st.text_input("To")
        weight = st.number_input("Weight", min_value=1, step=1)
        add_reverse = st.checkbox("Add reverse edge", value=False)
        if st.button("Add Edge"):
            if node1 in G.nodes and node2 in G.nodes:
                if G.has_edge(node1, node2):
                    st.warning("Edge already exists.")
                else:
                    G.add_edge(node1, node2, weight=weight)
                    if add_reverse and not G.has_edge(node2, node1):
                        G.add_edge(node2, node1, weight=weight)
                    st.success(f"Edge {node1} ➔ {node2} added.")
            else:
                st.error("One or both nodes do not exist.")

def remove_node_ui():
    with st.sidebar.expander("🗑️ Remove Node"):
        if len(G.nodes) == 0:
            st.info("No nodes to remove.")
            return
        del_node = st.selectbox("Select node", options=list(G.nodes), key="delnode")
        if st.button("Remove Node"):
            G.remove_node(del_node)
            st.warning(f"Node '{del_node}' removed.")

def remove_edge_ui():
    with st.sidebar.expander("🗑️ Remove Edge"):
        if len(G.edges) == 0:
            st.info("No edges to remove.")
            return
        edge_list = list(G.edges)
        del_edge = st.selectbox("Select edge", options=edge_list, key="deledge")
        if st.button("Remove Edge"):
            G.remove_edge(*del_edge)
            st.warning(f"Edge {del_edge} removed.")

def load_sample_topology():
    if st.sidebar.button("📅 Load Sample Topology"):
        G.clear()
        G.add_weighted_edges_from([
            ("A", "B", 2), ("B", "C", 3), ("C", "D", 1),
            ("A", "D", 10), ("B", "D", 2)
        ])
        st.rerun()

def draw_pyvis(G, path=None):
    net = Network(height="500px", directed=True)
    for node in G.nodes:
        net.add_node(node, label=node)
    for u, v, data in G.edges(data=True):
        color = "green" if path and (u, v) in zip(path, path[1:]) else "gray"
        net.add_edge(u, v, value=1, label=str(data['weight']), color=color)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.write_html(temp_file.name)
    return temp_file.name

def simulate_routing(G, source, destination, protocol):
    if protocol == "Dijkstra (OSPF)":
        path = nx.dijkstra_path(G, source=source, target=destination, weight='weight')
        cost = nx.dijkstra_path_length(G, source=source, target=destination, weight='weight')
    else:
        path = nx.bellman_ford_path(G, source=source, target=destination, weight='weight')
        cost = nx.bellman_ford_path_length(G, source=source, target=destination, weight='weight')
    return path, cost

def generate_routing_table(G, source, protocol):
    table = []
    for node in G.nodes:
        if node != source:
            try:
                if protocol == "Dijkstra (OSPF)":
                    p = nx.dijkstra_path(G, source, node, weight='weight')
                    dist = nx.dijkstra_path_length(G, source, node, weight='weight')
                else:
                    p = nx.bellman_ford_path(G, source, node, weight='weight')
                    dist = nx.bellman_ford_path_length(G, source, node, weight='weight')
                next_hop = p[1] if len(p) > 1 else "-"
                table.append((node, next_hop, dist, " ➔ ".join(p)))
            except:
                table.append((node, "-", "∞", "No path"))
    df = pd.DataFrame(table, columns=["Destination", "Next Hop", "Cost", "Path"])
    return df

def generate_gif_from_path(G, path, filename="routing_animation.gif"):
    frames = []
    pos = nx.spring_layout(G, seed=42)

    for i in range(1, len(path)+1):
        fig, ax = plt.subplots(figsize=(6, 4))
        nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", ax=ax)

        sub_path = list(zip(path[:i-1], path[1:i]))
        nx.draw_networkx_edges(G, pos, edgelist=sub_path, edge_color="red", width=2, ax=ax)

        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name, bbox_inches="tight")
        frames.append(imageio.imread(temp_file.name))
        plt.close()

    gif_path = os.path.join(tempfile.gettempdir(), filename)
    imageio.mimsave(gif_path, frames, duration=0.8)
    return gif_path

# --- UI Components ---
add_node_ui()
add_edge_ui()
remove_node_ui()
remove_edge_ui()
load_sample_topology()

# --- Routing Simulation ---
st.sidebar.header("Routing Settings")
protocol = st.sidebar.selectbox("Routing Protocol", ["Dijkstra (OSPF)", "Bellman-Ford (RIP)"])
nodes = list(G.nodes)

if len(nodes) < 2:
    st.info("Add at least two nodes to simulate routing.")
    st.stop()

source = st.sidebar.selectbox("Source", nodes)
destination = st.sidebar.selectbox("Destination", nodes)

try:
    path, cost = simulate_routing(G, source, destination, protocol)
    html_path = draw_pyvis(G, path)
    components.html(open(html_path, "r", encoding="utf-8").read(), height=550)
    os.remove(html_path)

    st.success(f"📍 Shortest Path: {' ➔ '.join(path)}")
    st.info(f"💰 Total Cost: {cost}")

    st.subheader(f"📄 Routing Table for {source}")
    df = generate_routing_table(G, source, protocol)
    st.dataframe(df, use_container_width=True)

    if st.checkbox("📘 Show forwarding tables for all routers"):
        for router in G.nodes:
            if len(G[router]) == 0:
                continue
            st.markdown(f"#### 📑 Router: {router}")
            table_df = generate_routing_table(G, router, protocol)
            st.dataframe(table_df, use_container_width=True)

    if st.button("📤 Export all routing tables to CSV"):
        all_tables = pd.DataFrame()
        for router in G.nodes:
            df_r = generate_routing_table(G, router, protocol)
            df_r.insert(0, "Router", router)
            all_tables = pd.concat([all_tables, df_r], ignore_index=True)

        csv = all_tables.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="routing_tables.csv", mime="text/csv")

    if st.button("🎞️ Export Path Animation as GIF"):
        gif_path = generate_gif_from_path(G, path)
        with open(gif_path, "rb") as f:
            st.download_button("⬇️ Download Path GIF", f, file_name="routing_path.gif", mime="image/gif")

except nx.NetworkXNoPath:
    st.error(f"🚫 No path exists from {source} to {destination}.")

st.markdown("---")
st.caption("💡 Made by Hira — Computer Networking Visualization with Streamlit + Pyvis")
