# ST_Hanna-Choi_Digital-Appendix
Digital appendix: a Neo4j graph schema and pipeline for SysML sequence diagrams, supporting automated analysis of True Model-Based Requirements (TUM semester thesis).

# A Graph Schema for SysML Sequence Diagrams to Enable Automated Analysis of True Model-Based Requirements

Digital appendix for the semester thesis by Hanna Choi, Chair of Spacecraft Systems, TUM School of Engineering and Design, Technical University of Munich.

Supervisor: Jaspar Sindermann. Examiner: Prof. Dr. Alessandro Golkar.

This repository contains the code, the Cypher queries, and the MagicDraw models used in the thesis. It extends the existing SysML-to-graph schema to SysML sequence diagrams, loading them into a Neo4j labelled property graph for automated analysis.

## Repository structure

| Path | Contents |
|------|----------|
| `extraction/` | `retrieve_SysML_model_HC.py` — parses a MagicDraw XMI export (`.mdxml`) into an intermediate JSON file. |
| `loading/` | `insert_sequence_diagram.py` — loads the JSON into Neo4j using parameterised Cypher `MERGE` statements. |
| `queries/analysis/` | Cypher queries for the structural and cross-diagram analysis (Appendix B.1–B.9). |
| `queries/tmbr/` | Cypher queries for the mode setup and natural-language requirement generation (Appendix B.10–B.14). |
| `MagicDraw_Models/` | The MagicDraw models used in the thesis, as `.mdxml` exports. |

## Pipeline

1. Export the SysML model from MagicDraw as an XMI file (`.mdxml`).
2. Run the extractor to produce the intermediate JSON:
   python extraction/retrieve_SysML_model_HC.py
   Set `FILE_NAME` at the top of the script to the model you want to process.
4. Run the loader to insert the graph into Neo4j:
   python loading/insert_sequence_diagram.py
4. Open the Neo4j Browser and run the queries in `queries/` to reproduce the analyses and the generated requirements.

## Requirements

- Python 3
- Neo4j (the `neo4j` Python driver for the loader)
- A SysML model exported from MagicDraw / Cameo Systems Modeler as XMI

## Models included

| File | Used for |
|------|----------|
| `ST_sd_Smartlight.mdxml` | Teaching example (Chapter 3). |
| `ST_sd_Satellite.mdxml` | Satellite update case study (Chapter 5). |
| `ST_2sd_Satellite.mdxml` | Two-diagram model for cross-diagram analysis (Section 5.2.2). |
| `ST_sd_wach2019autogen.mdxml` | Reproduction of the optical-instrument case of Salado and Wach (Section 6.3.2). |
