#!/usr/bin/env python3
"""
Salva o ID de um notebook da Cati para reuso futuro.
Uso: python3 save_notebook.py <notebook_id> <materia> <tema>
"""
import json
import sys
import os
from datetime import datetime

NOTEBOOKS_FILE = "/tmp/cati-prova/notebooks.json"

def save(notebook_id, materia, tema):
    os.makedirs("/tmp/cati-prova", exist_ok=True)
    
    notebooks = {}
    if os.path.exists(NOTEBOOKS_FILE):
        with open(NOTEBOOKS_FILE) as f:
            notebooks = json.load(f)
    
    key = f"{materia.lower()}:{tema.lower()}"
    notebooks[key] = {
        "id": notebook_id,
        "materia": materia,
        "tema": tema,
        "criado_em": datetime.now().isoformat()
    }
    
    with open(NOTEBOOKS_FILE, "w") as f:
        json.dump(notebooks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Notebook salvo: {key} → {notebook_id}")

def find(materia, tema):
    if not os.path.exists(NOTEBOOKS_FILE):
        return None
    with open(NOTEBOOKS_FILE) as f:
        notebooks = json.load(f)
    key = f"{materia.lower()}:{tema.lower()}"
    return notebooks.get(key)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        save(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        result = find(sys.argv[1], sys.argv[2])
        if result:
            print(f"Notebook encontrado: {result['id']} (criado em {result['criado_em']})")
        else:
            print("Notebook não encontrado — criar novo.")
    else:
        print("Uso: save_notebook.py <id> <materia> <tema>  (salvar)")
        print("     save_notebook.py <materia> <tema>        (buscar)")
