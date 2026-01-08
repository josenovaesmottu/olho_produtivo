def get_progress_color(ratio):
    """Retorna cor: vermelho (<40%), amarelo (40-80%), verde (>80%)"""
    if ratio < 0.4:
        return "#dc3545"  # Vermelho
    elif ratio < 0.8:
        return "#ffc107"  # Amarelo
    else:
        return "#28a745"  # Verde

def safe_divide(numerator, denominator):
    try:
        return numerator / denominator
    except Exception as e:
        return 0

def ordem_rampas(rampa):
    # Prioridade 1: Box rápido (0)
    # Prioridade 2: Cliente (1)
    # Prioridade 3: Interna (2)
    if rampa.get("box_rapido", False):
        return 0
    elif rampa.get("tipo_manutencao") == "Cliente":
        return 1
    else:
        return 2
