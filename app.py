import streamlit as st
import os
import json
import re                 
import shutil                         
import streamlit.components.v1 as components
from utils.scraper import kaggle_summary
from agents.researcher import DeepResearchAgent
from agents.strategist import StrategyAgent 
from agents.debugger import DebuggerAgent

def render_mermaid(mermaid_code):
    """Injects Mermaid.js into Streamlit to render flowcharts in dark mode."""
    # Clean up any weird invisible whitespace the AI generated
    clean_code = mermaid_code.strip()
    
    # We use await mermaid.run() to force execution, bypassing iframe loading quirks!
    html_code = f"""
<body style="background-color: transparent; margin: 0; padding: 0; display: flex; justify-content: center;">
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ theme: 'dark' }});
        await mermaid.run({{ querySelector: '.mermaid' }});
    </script>
    <pre class="mermaid">
{clean_code}
    </pre>
</body>
"""
    components.html(html_code, height=650, scrolling=True)

st.set_page_config(page_title="KaggleMind", layout="wide")
# --- INJECT CUSTOM CSS FOR SEAMLESS SIDEBAR NAVIGATION ---
# --- INJECT CUSTOM CSS FOR SEAMLESS SIDEBAR NAVIGATION ---
st.markdown("""
    <style>
    /* 1. Strip borders and backgrounds from ALL buttons in the history rows */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }

    /* 2. Style the Active Chat (Primary Button) so it looks like a highlighted pill */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.1) !important; 
        font-weight: bold !important;
        border-radius: 0.4rem !important;
    }

    /* 3. Add a soft hover effect for inactive chats */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 0.4rem !important;
    }

    /* 4. Completely eliminate the column gap to merge them */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: center !important;
        margin-bottom: 0.2rem !important; 
    }

    /* 5. Make the 3-dots subtle and centered */
    [data-testid="stSidebar"] [data-testid="stPopover"] > button {
        color: #888 !important; 
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stPopover"] > button:hover {
        color: #fff !important; 
    }

    /* 6. HIDE THE DROPDOWN CHEVRON ARROW */
    [data-testid="stSidebar"] [data-testid="stPopover"] button svg,
    [data-testid="stSidebar"] [data-testid="stPopover"] button div:nth-of-type(2),
    [data-testid="stSidebar"] [data-testid="stPopover"] button::after,
    [data-testid="stSidebar"] [data-testid="stPopover"] button::before {
        display: none !important;
        opacity: 0 !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        visibility: hidden !important;
    } 
    </style>
""", unsafe_allow_html=True)

if not os.path.exists("storage"):
    os.makedirs("storage")

#STATE & SIDEBAR ARCHITECTURE
all_folders = [f for f in os.listdir("storage") if os.path.isdir(os.path.join("storage", f))]

past_comps = sorted(
    all_folders, 
    key=lambda x: os.path.getctime(os.path.join("storage", x)), 
    reverse=True
)

comp_mapping = {}    
slug_to_name = {}    
  
for slug in past_comps:
    meta_path = f"storage/{slug}/metadata.json"
    clean_name = slug.replace("-", " ").title()
    
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
                clean_name = meta_data.get("title", clean_name)
        except Exception:
            pass
            
    comp_mapping[clean_name] = slug
    slug_to_name[slug] = clean_name

if "active_slug" not in st.session_state:
    st.session_state.active_slug = "New Competition"

st.sidebar.markdown("### Your Research Chats")

is_new_active = (st.session_state.active_slug == "New Competition")
if st.sidebar.button("➕ New Competition", use_container_width=True, type="primary" if is_new_active else "secondary"):
    st.session_state.active_slug = "New Competition"
    st.rerun()

st.sidebar.divider()

for display_name, slug in comp_mapping.items():
    nav_col, dot_col = st.sidebar.columns([8.5, 1.5])
    
    with nav_col:
        is_active = (st.session_state.active_slug == slug)
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(f"{display_name}", key=f"nav_{slug}", use_container_width=True, type=btn_type):
            st.session_state.active_slug = slug
            st.rerun()
            
    with dot_col:
        with st.popover("⋮", use_container_width=True):
            st.markdown(f"Delete **{display_name}**?")
            if st.button("Confirm", key=f"del_{slug}", type="primary", use_container_width=True):
                shutil.rmtree(f"storage/{slug}", ignore_errors=True)
                if st.session_state.active_slug == slug:
                    st.session_state.active_slug = "New Competition"
                st.rerun()

chosen_display = slug_to_name.get(st.session_state.active_slug, "➕ New Competition")


# 2. MAIN WORKSPACE UI
st.title("KaggleMind: Deep Research Agent")
st.divider()

if st.session_state.active_slug == "New Competition":
    url = st.text_input("Paste Kaggle Competition URL:", placeholder="https://www.kaggle.com/competitions/...")
    
    if st.button("Start Research", type="primary") and url:
        with st.spinner("🕵️ Agent 1: Scouring forums and metadata..."):
            try:
                scraped_data = kaggle_summary(url)
                comp_slug = scraped_data['slug']
                
                researcher = DeepResearchAgent()
                dossier = researcher.generate_dossier(comp_slug, scraped_data['markdown'])
                
                path = f"storage/{comp_slug}"
                if not os.path.exists(path):
                    os.makedirs(path)
                    
                with open(f"{path}/dossier.md", "w", encoding="utf-8") as f:
                    f.write(dossier)
                
                nice_title = comp_slug.replace("-", " ").title()
                with open(f"{path}/metadata.json", "w", encoding="utf-8") as f:
                    json.dump({"title": nice_title, "slug": comp_slug}, f)
                
                st.session_state.active_slug = comp_slug
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred during research: {str(e)}")

else:
    active_slug = st.session_state.active_slug
    dossier_path = f"storage/{active_slug}/dossier.md"
    strat_hist_path = f"storage/{active_slug}/chat_hist.json"
    code_hist_path = f"storage/{active_slug}/code_chat_hist.json"
    
    st.header(f" {chosen_display}")
    
    tab1, tab2, tab3 = st.tabs(["📑 Research Dossier", "⚔️ Strategy War Room", "💻 Code Co-Pilot"])
    
    with tab1:
        if os.path.exists(dossier_path):
            with open(dossier_path, "r", encoding="utf-8") as f:        
                dossier_content = f.read()
            st.markdown(dossier_content)
        else:
            st.error("Dossier data file not found.")
            dossier_content = ""

    with tab2:
        if os.path.exists(strat_hist_path):
            with open(strat_hist_path, "r", encoding="utf-8") as f:
                strat_history = json.load(f)
        else:
            strat_history = []

        col2_a, col2_b = st.columns([5, 1])
        with col2_a:
            st.caption("Brainstorm and refine your high-level training and cross-validation strategies here.")
        with col2_b:
            if strat_history and st.button("Clear", key="clear_strat", type="secondary"):
                os.remove(strat_hist_path)
                st.rerun()

        st.divider()

        for msg in strat_history:
            with st.chat_message(msg["role"]):
                display_text = msg["content"]
                
                # Check if it's the AI and if it contains a mermaid block
                if msg["role"] == "assistant":
                    mermaid_match = re.search(r'```mermaid\n(.*?)\n```', display_text, re.DOTALL)
                    
                    if mermaid_match:
                        # Strip the raw code block out of the text so it doesn't double-print
                        display_text = re.sub(r'```mermaid\n.*?\n```', '\n\n*( Architecture Flowchart Generated)*\n', display_text, flags=re.DOTALL)
                        st.markdown(display_text)
                        
                        # Render the actual visual graph
                        render_mermaid(mermaid_match.group(1))
                    else:
                        st.markdown(display_text)
                else:
                    st.markdown(display_text)
                
        strat_proposal = st.chat_input("Discuss your strategy parameters...", key="strat_chat_input")
        
        # 2. Render new messages live
        if strat_proposal:
            strat_history.append({"role": "user", "content": strat_proposal})
            
            with st.spinner("🤖 Grandmaster Strategist is mapping the architecture..."):
                strategist = StrategyAgent()
                agent_critique = strategist.review_proposal(dossier_content, strat_history[:-1], strat_proposal)
                
            strat_history.append({"role": "assistant", "content": agent_critique})
            
            with open(strat_hist_path, "w", encoding="utf-8") as f:
                json.dump(strat_history, f, indent=4)
            st.rerun()
            
    with tab3:
        if os.path.exists(code_hist_path):
            with open(code_hist_path, "r", encoding="utf-8") as f:
                code_history = json.load(f)
        else:
            code_history = []
            
        if "active_code" not in st.session_state:
            st.session_state.active_code = ""
        if "active_file_name" not in st.session_state:
            st.session_state.active_file_name = ""
            
        def extract_code_from_ipynb(file_bytes):
            try:
                notebook = json.loads(file_bytes.decode('utf-8'))
                code_cells = []
                for cell in notebook.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        cell_content = "".join(cell.get('source', []))
                        if cell_content.strip():
                            code_cells.append(cell_content)
                return "\n\n# --- NEXT CELL ---\n\n".join(code_cells)
            except Exception as e:
                return f"# Error parsing notebook: {str(e)}"

        col3_a, col3_b = st.columns([5, 1])
        with col3_a:
            if st.session_state.active_code:
                with st.expander(f"👀 Active File Context: {st.session_state.active_file_name}"):
                    st.code(st.session_state.active_code, language="python")
            else:
                st.info("No active file. Use the paperclip icon in the chat box below to upload a script!")
        with col3_b:
            if code_history or st.session_state.active_code:
                if st.button("🧹 Clear Chat", key="clear_code", type="secondary"):
                    if os.path.exists(code_hist_path):
                        os.remove(code_hist_path)
                    st.session_state.active_code = ""
                    st.session_state.active_file_name = ""
                    st.rerun()

        st.divider()

        chat_container = st.container(height=500)
        with chat_container:
            if not code_history:
                st.caption("👋 Welcome to the Code Studio! Upload a .py or .ipynb file via the chat bar, or paste a terminal error to get started.")
            for msg in code_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input(
            "Ask a question, paste an error, or upload a script...", 
            key="code_chat_input", 
            accept_file=True, 
            file_type=["py", "ipynb"]
        )
        
        if prompt:
            if isinstance(prompt, str):
                user_text = prompt
                uploaded_files = []
            else:
                user_text = getattr(prompt, "text", "")
                uploaded_files = getattr(prompt, "files", [])
            
            if uploaded_files:
                file = uploaded_files[0]
                st.session_state.active_file_name = file.name
                if file.name.endswith('.ipynb'):
                    st.session_state.active_code = extract_code_from_ipynb(file.getvalue())
                else:
                    st.session_state.active_code = file.getvalue().decode("utf-8")
                
                if not user_text.strip():
                    user_text = f"I have uploaded my script `{file.name}`. Could you review it against our strategy?"
            
            if user_text.strip():
                code_history.append({"role": "user", "content": user_text})
                
                with st.spinner("🤖 Co-pilot is evaluating..."):
                    copilot = DebuggerAgent()
                    copilot_response = copilot.chat_with_copilot(
                        dossier_content, 
                        st.session_state.active_code, 
                        code_history[:-1], 
                        user_text
                    )
                
                code_history.append({"role": "assistant", "content": copilot_response})
                
                with open(code_hist_path, "w", encoding="utf-8") as f:
                    json.dump(code_history, f, indent=4)
                st.rerun()