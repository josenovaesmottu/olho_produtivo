import json
from pathlib import Path

def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return float(value)
    except (ValueError, TypeError):
        return None

def compilar_filiais():
    raw_filiais_path = Path(__file__).parent / "raw_filiais.json"
    output_path = Path(__file__).parent / "filiais.json"

    with raw_filiais_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    resultado: dict[str, list] = {}
    for item in raw:
        gerente = item.get("gerente_regional")
        
        filial = {
            "nome": item.get("lugar"),
            "id":item.get("lugarid"),
            "meta_interna": safe_int(item.get("meta_internas")),
            "meta_rampa": safe_int(item.get("mec_rampa_ideal"))
        }
        
        if gerente not in resultado:
            resultado[gerente] = []
        resultado[gerente].append(filial)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

compilar_filiais()