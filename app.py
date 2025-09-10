import streamlit as st
import pandas as pd

# Read your Excel file
df_orders = pd.read_excel("Disney_HR.xlsx")

for i in range(1, 6):
	df_orders[f"L{i}"] = df_orders["Org_String_Abbrev"].str.split("/").str[i - 1]

unique_L1 = sorted(df_orders["L1"].dropna().unique())

st.set_page_config(layout="wide")

# Character_Name		Org_String_Abbrev
# Mickey Mouse			DIS/MMF/MC
# Sulley				DIS/MI/MC
# Simba					DIS/TLK/MC


# Track the currently selected path
if "active_path" not in st.session_state:
    st.session_state.active_path = []

# Helper to make a centered button with unique keys
def centered_button(label, path, prefix="node"):
    left, center, right = st.columns([1, 2, 1])
    key = f"{prefix}_L{len(path)}_" + "_".join(path + [label])
    with center:
        return st.button(label, key=key, use_container_width=True)

# --- Default view: show all L1s ---
if not st.session_state.active_path:
    unique_L1 = sorted(df_orders["L1"].dropna().unique())
    l1_cols = st.columns(len(unique_L1))
    for col, l1 in zip(l1_cols, unique_L1):
        with col:
            clicked = centered_button(l1, path=[], prefix="child")
            if clicked:
                st.session_state.active_path = [l1]

# --- Active path exists ---
else:
    # --- Show full ancestry ---
    for i, node in enumerate(st.session_state.active_path):
        col = st.columns(1)[0]
        with col:
            clicked = centered_button(node, path=st.session_state.active_path[:i], prefix="ancestor")
            if clicked:
                st.session_state.active_path = st.session_state.active_path[:i+1]

    # --- Show children of the last node ---
    level = len(st.session_state.active_path)
    next_level = f"L{level+1}"

    df_filtered = df_orders.copy()
    for i, ancestor in enumerate(st.session_state.active_path):
        df_filtered = df_filtered[df_filtered[f"L{i+1}"] == ancestor]

    children = sorted(df_filtered[next_level].dropna().unique())
    if children:
        subcols = st.columns(len(children))
        for subcol, child in zip(subcols, children):
            with subcol:
                clicked = centered_button(child, path=st.session_state.active_path, prefix="child")
                if clicked:
                    st.session_state.active_path.append(child)

# --- Display table for current node only (exact matches) ---
if st.session_state.active_path:
    level = len(st.session_state.active_path)
    current_node = st.session_state.active_path[-1]

    # Start filtering for the exact node
    df_current = df_orders.copy()
    for i, ancestor in enumerate(st.session_state.active_path):
        df_current = df_current[df_current[f"L{i+1}"] == ancestor]

    # Remove rows where deeper levels exist
    for deeper_level in range(level + 1, 6):
        df_current = df_current[df_current[f"L{deeper_level}"].isna()]

    st.write(f"**Data for {current_node} (exact level only):**")
    st.dataframe(df_current)

# streamlit run app.py