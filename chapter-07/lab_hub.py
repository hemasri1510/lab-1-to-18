# lab_hub.py - Runs all Labs 8 to 18 and shows RESULTS in website
import os, subprocess, sys
import streamlit as st

def show_lab_hub():
    st.header("🧪 All Labs 8 to 18 - Live Results")

    base = os.path.dirname(__file__)
    repo = os.path.dirname(base)

    for num in range(8, 19):
        folder = os.path.join(repo, f"chapter-{num:02d}")
        if not os.path.exists(folder):
            continue

        st.subheader(f"Experiment {num}")
        files = [f for f in os.listdir(folder) if f.endswith(".py")]

        if not files:
            st.write("No python files found")
            continue

        for f in files:
            path = os.path.join(folder, f)
            st.write(f"📄 {f}")
            try:
                # Run the lab file and capture its printed result
                result = subprocess.run(
                    [sys.executable, path],
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout or result.stderr or "No output"
                st.code(output[:2000])
            except Exception as e:
                st.error(f"Error: {e}")