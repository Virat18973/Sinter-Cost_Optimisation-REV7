# Sinter Burden Control — Industrial Dashboard V7

Production-oriented Streamlit UI for the sinter burden optimization model.

## Files
- `app.py` — Streamlit interface
- `optimizer.py` — optimization engine
- `requirements.txt` — deployment dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud
Set `app.py` as the main file. The optimizer uses the built-in master chemistry by default; Excel upload is optional.

## Design goals
Graphite/steel industrial palette, clear operational status, editable commercial inputs, quality gate, manual burden control, scenario analysis, bottleneck view, cost/burden composition and export.
