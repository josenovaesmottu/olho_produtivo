def get_progress_color(ratio):
    """Retorna cor: vermelho (<40%), amarelo (40-80%), verde (>80%)"""
    if ratio < 0.5:
        return "#dc3545"  # Vermelho
    elif ratio >= 1:
        return  "#28a745"  # Verde
    else:
        return "#ffc107"  # Amarelo

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

def safe_int(value, default=0):
    """Converte valor para inteiro de forma segura, retornando default em caso de erro"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def format_time_delta(ultima_atividade):
    """Calcula e formata o delta de tempo entre agora e a última atividade"""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    if not ultima_atividade or ultima_atividade == "Erro":
        return "sem atividade"
    
    try:
        # Converter string ISO para datetime
        ultima_dt = datetime.fromisoformat(ultima_atividade.replace('Z', '+00:00'))
        # Obter datetime atual em São Paulo
        agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
        
        # Calcular diferença
        delta = agora - ultima_dt
        
        # Formatar delta
        if delta.days > 0:
            return f"{delta.days}d {delta.seconds // 3600}h"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
        else:
            return f"{(delta.seconds % 3600) // 60}m"
    except Exception:
        return "formato inválido"
