# Part 2: Prototype Task - Extract & Route Deliverables

This repository serves as a response to the Part 2 of the COE Assignment. It contains the code and documentation for the prototype task that extracts and routes deliverables from a contract text.

1. main.py
This script serves as a basic POC for the core functionality.

```bash
pip install -r requirements.txt
python main.py
```

2. server.py
This file creates a simple API that can be continuously running to listen for incoming requests. To run it, we need two terminals:

A) Server Side
```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

B) Client Side
To simulate Monday.com webhook:
```bash
curl -X POST http://localhost:8000/webhook/monday \
-H "Content-Type: application/json" \
-d '{"text": "Create a branded booth for the annual conference by 2025-12-01. Assign to the EVENTS team. Also, prepare marketing materials for the campaign, assigned to MARKETING, due by 2025-11-15."}'
```


To simulate HubSpot.com webhook:
```bash
curl -X POST http://localhost:8000/webhook/hubspot \
-H "Content-Type: application/json" \
-d '{"text": "Create a branded booth for the annual conference by 2025-12-01. Assign to the EVENTS team. Also, prepare marketing materials for the campaign, assigned to MARKETING, due by 2025-11-15."}'
```

3. langg.py
This file serves as an implementation if the LangGraph library were to be used.

```bash
pip install -r requirements.txt
python langg.py
```
