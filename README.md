# KaggleMind 

**KaggleMind** is a personal, multi-agent AI framework designed to act as an autonomous co-pilot for machine learning and data science competitions. 

> **Note:** This repository is an archival portfolio piece. It is not packaged, maintained, or intended for public installation or use.

##  System Architecture

Built with Streamlit and LangChain, the application breaks away from rigid, linear workflows. It provides a fluid, open-workspace environment where underlying agents maintain decoupled execution contexts while sharing a live background memory bridge.

The system is divided into three core operational phases:

### 1. Phase 1: Deep Research
* **Function:** Automatically ingests and scrapes raw Kaggle competition URLs.
* **Output:** Generates a definitive, ground-truth markdown dossier mapping out the data schema, evaluation metrics (e.g., LogLoss vs. QWK), and competition rules to prevent LLM hallucinations down the line.

### 2. Phase 2: Strategy War Room
* **Function:** An interactive ML Architect agent interface.
* **Output:** Brainstorms and records cross-validation configurations, feature engineering pipelines, and class imbalance strategies, saving the architectural state to a dedicated memory file.

### 3. Phase 3: Code Co-Pilot
* **Function:** A conversational implementation engine.
* **Output:** Parses uploaded `.py` scripts and heavily nested `.ipynb` Jupyter notebooks. It reads the active code alongside the live strategy chat history from Phase 2, immediately identifying if the current implementation deviates from the planned architectural strategy.

##  Tech Stack
* **UI/UX:** Streamlit
* **Agentic Orchestration:** LangChain 
* **LLM Foundations:** Gemini 
