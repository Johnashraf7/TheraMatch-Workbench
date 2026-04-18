from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import networkx as nx

import open_targets
import pollinations

app = FastAPI(title="TheraMatch API", description="Computational Drug Repurposing Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExplainRequest(BaseModel):
    drug: str
    disease: str
    genes: list[str]

@app.get("/")
def read_root():
    return {"message": "Welcome to TheraMatch Engine Backend"}

@app.get("/api/search")
def search_disease(query: str):
    results = open_targets.search_disease(query)
    return {"results": results}

@app.get("/api/predict")
def predict_repurposing(disease_id: str, disease_name: str):
    # 1. Get targets
    targets = open_targets.get_targets_for_disease(disease_id, size=50)
    if not targets:
        raise HTTPException(status_code=404, detail="No targets found for this disease")
    
    target_ids = [t["id"] for t in targets]
    
    # 2. Get drugs
    drugs_dict = open_targets.get_drugs_for_targets(target_ids)
    if not drugs_dict:
        raise HTTPException(status_code=404, detail="No interacting drugs found")
        
    # 3. Build Graph & Score
    G = nx.Graph()
    
    # Add disease node
    G.add_node(disease_name, type="disease")
    
    # Add gene nodes and edges to disease
    for t in targets:
        symbol = t["symbol"]
        score = t["score"]
        G.add_node(symbol, type="gene")
        G.add_edge(disease_name, symbol, weight=score)
        
    # Add drug nodes and edges to genes
    for drug_id, d_data in drugs_dict.items():
        drug_name = d_data["name"]
        t_symbols = d_data["targets"]
        G.add_node(drug_name, type="drug", id=drug_id)
        for t_sym in t_symbols:
            if t_sym in G:
                G.add_edge(drug_name, t_sym)
                
    # Proximity Scoring
    drug_scores = []
    
    for node, data in G.nodes(data=True):
        if data.get("type") == "drug":
            score = 0.0
            shared_genes = []
            
            # neighbors of drug are genes
            for neighbor in G.neighbors(node):
                if G.nodes[neighbor].get("type") == "gene":
                    # add the weight of the gene-disease edge
                    if G.has_edge(disease_name, neighbor):
                        edge_data = G.get_edge_data(disease_name, neighbor)
                        weight = edge_data.get("weight", 0.0)
                        score += weight
                        shared_genes.append(neighbor)
                        
            if score > 0:
                drug_scores.append({
                    "id": data.get("id"),
                    "name": node,
                    "score": round(score, 4),
                    "shared_genes": shared_genes
                })
                
    # Sort and return top 20
    drug_scores.sort(key=lambda x: x["score"], reverse=True)
    top_candidates = drug_scores[:20]
    
    return {
        "disease": disease_name,
        "disease_id": disease_id,
        "candidates": top_candidates
    }

@app.post("/api/explain")
def explain_mechanism(req: ExplainRequest):
    explanation = pollinations.generate_explanation(req.drug, req.disease, req.genes)
    return {"explanation": explanation}
