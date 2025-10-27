import streamlit as st
import networkx as nx
import pandas as pd
import numpy as np
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import ui

# Set page configuration
st.set_page_config(page_title="Routing Simulator with Animation", layout="wide")
st.title("🌐 Interactive Routing Protocol Simulator")

# Initialize session state values
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# UI: dark mode toggle in the sidebar (updates st.session_state.dark_mode)
with st.sidebar:
    st.checkbox("🌙 Dark mode", value=st.session_state.dark_mode, key='dark_mode', help='Toggle dark theme')

# inject global theme and UI helpers (use current dark preference)
ui.inject_theme(st.session_state.dark_mode)

# Initialize session state graph
if 'G' not in st.session_state:
    st.session_state.G = nx.DiGraph()
G = st.session_state.G

# --- Functions ---
def add_node_ui():
    with st.sidebar.expander("➕ Add Node"):
        # Use a form so the text input and submit are grouped and don't
        # trigger intermediate reruns that lose focus.
        with st.form(key="form_add_node", clear_on_submit=True):
            new_node = st.text_input("Node name", key="add_node_name")
            submitted = st.form_submit_button("Add Node")
            if submitted:
                if not new_node or new_node.strip() == "":
                    st.error("Please enter a valid node name.")
                else:
                    if new_node in G.nodes:
                        st.warning("Node already exists.")
                    else:
                        G.add_node(new_node)
                        ui.toast(f"Node '{new_node}' added.", kind='success')

def add_edge_ui():
    with st.sidebar.expander("➕ Add Edge"):
        # Group edge inputs into a form to avoid partial reruns while selecting
        # nodes; this improves focus and reliability.
        with st.form(key="form_add_edge", clear_on_submit=True):
            node_options = list(G.nodes) if len(G.nodes) else [""]
            node1 = st.selectbox("From", options=node_options, key="edge_from")
            node2 = st.selectbox("To", options=node_options, key="edge_to")
            weight = st.number_input("Weight", min_value=1, step=1, value=1, key='edge_weight')
            add_reverse = st.checkbox("Add reverse edge", value=False, key='edge_reverse')
            submitted = st.form_submit_button("Add Edge")
            if submitted:
                if not node1 or not node2:
                    st.error("Select both endpoints.")
                elif node1 == node2:
                    st.error("Cannot create self-loop.")
                elif node1 in G.nodes and node2 in G.nodes:
                    if G.has_edge(node1, node2):
                        st.warning("Edge already exists.")
                    else:
                        G.add_edge(node1, node2, weight=weight)
                        if add_reverse and not G.has_edge(node2, node1):
                            G.add_edge(node2, node1, weight=weight)
                        ui.toast(f"Edge {node1} → {node2} added.", kind='success')
                else:
                    st.error("One or both nodes do not exist.")

def remove_node_ui():
    with st.sidebar.expander("🗑️ Remove Node"):
        if len(G.nodes) == 0:
            st.info("No nodes to remove.")
            return
        with st.form(key="form_remove_node"):
            del_node = st.selectbox("Select node", options=list(G.nodes), key="delnode")
            confirm = st.checkbox(f"Confirm remove '{del_node}'", key='confirm_remove_node')
            submitted = st.form_submit_button("Remove Node")
            if submitted:
                if confirm:
                    if del_node in G.nodes:
                        G.remove_node(del_node)
                        ui.toast(f"Node '{del_node}' removed.", kind='warn')
                    else:
                        st.error("Selected node no longer exists.")
                else:
                    st.info("Check the confirm box to remove the node.")

def remove_edge_ui():
    with st.sidebar.expander("🗑️ Remove Edge"):
        if len(G.edges) == 0:
            st.info("No edges to remove.")
            return
        edge_list = [f"{u} -> {v}" for u, v in G.edges]
        with st.form(key="form_remove_edge"):
            del_edge = st.selectbox("Select edge", options=edge_list, key="deledge")
            confirm = st.checkbox(f"Confirm remove '{del_edge}'", key='confirm_remove_edge')
            submitted = st.form_submit_button("Remove Edge")
            if submitted:
                if confirm:
                    u, v = del_edge.split(" -> ")
                    if G.has_edge(u, v):
                        G.remove_edge(u, v)
                        ui.toast(f"Edge {u} → {v} removed.", kind='warn')
                    else:
                        st.error("Selected edge no longer exists.")
                else:
                    st.info("Check the confirm box to remove the edge.")

def load_sample_topology():
    if st.sidebar.button("📅 Load Sample Topology"):
        G.clear()
        G.add_weighted_edges_from([
            ("A", "B", 2), ("B", "C", 3), ("C", "D", 1),
            ("A", "D", 10), ("B", "D", 2)
        ])
        st.success("Sample topology loaded.")
        ui.toast("Sample topology loaded", kind='info')
        # trigger a rerun only after the sample is loaded so the UI refreshes
        # and form controls keep focus during normal interaction.
        try:
            # prefer the stable API when available
            st.experimental_rerun()
        except Exception:
            # fallback to st.rerun if present in older Streamlit versions
            try:
                st.rerun()
            except Exception:
                pass

def draw_pyvis(G, path=None):
    net = Network(height="550px", width="100%", directed=True, bgcolor="#ffffff")
    net.barnes_hut()
    for node in G.nodes:
        net.add_node(node, label=node, title=node)
    # build set of edges in path for quick lookup
    path_edges = set()
    if path and len(path) > 1:
        path_edges = set(zip(path, path[1:]))

    for u, v, data in G.edges(data=True):
        color = "#2ecc71" if (u, v) in path_edges else "#95a5a6"
        width = 3 if (u, v) in path_edges else 1
        net.add_edge(u, v, value=data.get('weight', 1), label=str(data.get('weight', '')), color=color, width=width)

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
                table.append((node, next_hop, float(dist), " ➔ ".join(p)))
            except:
                table.append((node, "-", float('inf'), "No path"))
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
# --- UI Components (sidebar first) ---
add_node_ui()
add_edge_ui()
remove_node_ui()
remove_edge_ui()
load_sample_topology()

# --- Routing Simulation ---
st.sidebar.header("Routing Settings")
protocol = st.sidebar.selectbox("Routing Protocol", ["Dijkstra (OSPF)", "Bellman-Ford (RIP)"])
nodes = list(G.nodes)

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Tips**")
st.sidebar.write("- Add nodes and edges on the left.\n- Select source/destination below and run the simulation.\n- Export routing tables or GIFs for reports.")

if len(nodes) < 2:
    st.info("Add at least two nodes to simulate routing.")
    st.stop()

# Use radio buttons for small topologies (more reliably styled) and
# fall back to selectbox for larger lists to conserve vertical space.
if len(nodes) <= 10:
    source = st.sidebar.radio("Source", nodes, index=0)
    # choose a sensible default index for destination (not the same as source when possible)
    dest_index = 1 if len(nodes) > 1 else 0
    destination = st.sidebar.radio("Destination", nodes, index=dest_index)
else:
    source = st.sidebar.selectbox("Source", nodes)
    destination = st.sidebar.selectbox("Destination", nodes)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Network Topology")
    try:
        path, cost = simulate_routing(G, source, destination, protocol)
        html_path = draw_pyvis(G, path)
        with open(html_path, "r", encoding="utf-8") as f:
            components.html(f.read(), height=550)
        os.remove(html_path)

        st.success(f"📍 Shortest Path: {' ➔ '.join(path)}")
        st.info(f"💰 Total Cost: {cost}")

        # GIF export button
        if st.button("🎞️ Export Path Animation as GIF"):
            gif_path = generate_gif_from_path(G, path)
            with open(gif_path, "rb") as f:
                st.download_button("⬇️ Download Path GIF", f, file_name="routing_path.gif", mime="image/gif")

    except nx.NetworkXNoPath:
        st.error(f"🚫 No path exists from {source} to {destination}.")

with col2:
    st.subheader(f"📄 Routing Table ({source})")
    df = generate_routing_table(G, source, protocol)
    # convert inf to a printable symbol for display only to avoid Arrow serialization issues
    display_df = df.copy()
    display_df['Cost'] = display_df['Cost'].apply(lambda x: '∞' if np.isinf(x) else x)
    st.dataframe(display_df, use_container_width=True)

    if st.checkbox("📘 Show forwarding tables for all routers"):
        for router in G.nodes:
            if len(G[router]) == 0:
                continue
            st.markdown(f"#### 📑 Router: {router}")
            table_df = generate_routing_table(G, router, protocol)
            table_df_display = table_df.copy()
            table_df_display['Cost'] = table_df_display['Cost'].apply(lambda x: '∞' if np.isinf(x) else x)
            st.dataframe(table_df_display, use_container_width=True)

    if st.button("📤 Export all routing tables to CSV"):
        all_tables = pd.DataFrame()
        for router in G.nodes:
            df_r = generate_routing_table(G, router, protocol)
            df_r.insert(0, "Router", router)
            all_tables = pd.concat([all_tables, df_r], ignore_index=True)

        csv = all_tables.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="routing_tables.csv", mime="text/csv")

st.markdown("---")
st.caption("💡 Made by Lucky — Computer Networking Visualization with Streamlit + Pyvis")
