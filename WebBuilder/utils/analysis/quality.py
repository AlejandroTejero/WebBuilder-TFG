
from __future__ import annotations


# Cálculo de calidad del mapping
# Evalúa qué tan completo y correcto está el mapping configurado
def calculate_mapping_quality(field_mapping: dict, analysis_result: dict | None = None) -> dict:
    score = 0
    max_score = 100
    issues = []
    
    # +30 puntos: Tiene title (CRÍTICO)
    if field_mapping.get('title'):
        score += 30
    else:
        issues.append('⚠️ Falta título - es el campo más importante')
    
    # +20 puntos: Tiene description
    if field_mapping.get('description'):
        score += 20
    else:
        issues.append('⚠️ Falta descripción - ayuda a entender el contenido')
    
    # +15 puntos: Tiene image
    if field_mapping.get('image'):
        score += 15
    else:
        issues.append('💡 Considera agregar una imagen - hace la web más atractiva')
    
    # +10 puntos: Tiene link
    if field_mapping.get('link'):
        score += 10
    else:
        issues.append('💡 Agrega un enlace si quieres que los usuarios accedan al contenido original')
    
    # +10 puntos: Tiene date
    if field_mapping.get('date'):
        score += 10
    else:
        issues.append('💡 La fecha ayuda a contextualizar el contenido')
    
    # +5 puntos: Tiene author
    if field_mapping.get('author'):
        score += 5
    
    # +10 puntos: No hay duplicados en roles críticos
    critical_roles = ['title', 'description', 'content', 'subtitle', 'author']
    used_keys = {}
    has_duplicates = False
    
    for role in critical_roles:
        key = field_mapping.get(role)
        if key and key in used_keys:
            has_duplicates = True
            issues.append(
                f"❌ '{role}' y '{used_keys[key]}' usan el mismo campo '{key}' - "
                f"esto hará que se muestre contenido repetido"
            )
        elif key:
            used_keys[key] = role
    
    if not has_duplicates:
        score += 10
    
    # Clasificación por score
    if score >= 80:
        quality = 'Excelente'
        quality_emoji = '✅'
        color = 'green'
    elif score >= 60:
        quality = 'Bueno'
        quality_emoji = '👍'
        color = 'blue'
    elif score >= 40:
        quality = 'Aceptable'
        quality_emoji = '⚠️'
        color = 'orange'
    else:
        quality = 'Mejorable'
        quality_emoji = '❌'
        color = 'red'
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': score,  # Ya está en escala 0-100
        'quality': f'{quality} {quality_emoji}',
        'color': color,
        'issues': issues,
    }
