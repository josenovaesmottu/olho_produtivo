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