import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

st.title("Advanced Multiprocessor Network Simulator")
st.write("Simulate ICN topologies with adaptive routing, deadlock & livelock detection")

# Sidebar controls
topology = st.sidebar.selectbox("Choose Topology", ["Mesh", "Torus", "Hypercube"])
switching = st.sidebar.selectbox("Switching Technique", ["Circuit Switching", "Packet Switching", "Virtual Channel"])
nodes = st.sidebar.slider("Number of Nodes per Dimension", 2, 5, 3)
packets = st.sidebar.slider("Number of Packets", 1, 8, 3)
speed = st.sidebar.slider("Simulation Speed (s)", 0.1, 2.0, 0.5)

# Generate topology
def generate_topology(topology, n):
    if topology == "Mesh":
        G = nx.grid_2d_graph(n, n)
    elif topology == "Torus":
        G = nx.grid_2d_graph(n, n, periodic=True)
    else:  # Hypercube
        G = nx.hypercube_graph(n)
    return G

G = generate_topology(topology, nodes)
pos = nx.spring_layout(G, seed=42)

# Initialize packets
class Packet:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.current = src
        self.path = [src]
        self.completed = False
        self.blocked_steps = 0

packet_list = []
for _ in range(packets):
    src, dst = random.sample(list(G.nodes()), 2)
    packet_list.append(Packet(src, dst))

# Helper: get neighbors with least congestion
def adaptive_next_hop(packet):
    neighbors = list(G.neighbors(packet.current))
    neighbors = [n for n in neighbors if n not in packet.path]  # avoid loops
    if not neighbors:
        packet.blocked_steps += 1
        return packet.current  # deadlock/livelock
    return min(neighbors, key=lambda n: sum(1 for p in packet_list if p.current==n and not p.completed))

# Simulation loop
max_steps = nodes*nodes*2
for step in range(max_steps):
    plt.figure(figsize=(6,6))
    node_colors = []
    
    for node in G.nodes():
        packet_here = [p for p in packet_list if p.current==node and not p.completed]
        if not packet_here:
            node_colors.append('lightblue')
        else:
            if any(p.blocked_steps>=3 for p in packet_here):
                node_colors.append('orange')  # deadlock/livelock
            else:
                node_colors.append('red')  # active packet
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=600)

    # Move packets
    for p in packet_list:
        if p.completed:
            continue
        if p.current == p.dst:
            p.completed = True
            continue
        next_hop = adaptive_next_hop(p)
        p.current = next_hop
        p.path.append(next_hop)
    
    st.pyplot(plt)
    plt.clf()
    time.sleep(speed)

# Summary
st.write("### Simulation Summary")
st.write(f"Topology: {topology}")
st.write(f"Switching: {switching}")
st.write(f"Packets simulated: {packets}")
st.write("Legend: Red=Active, Orange=Deadlock/Livelock, Blue=Empty Node")
st.write("Packet paths and status:")
for idx, p in enumerate(packet_list):
    status = "Completed" if p.completed else "Blocked"
    st.write(f"Packet {idx+1}: {p.path} -> {status}")
