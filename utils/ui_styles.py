import markdown as md

def render_title(text: str) -> str:
    """
    Renderiza un título principal institucional.

    Args:
        text (str): Texto del título principal.

    Returns:
        str: HTML formateado con estilo institucional.
    """
    return f"""
    <h2 style="color:#0073E6; text-align:center; margin-top:10px; margin-bottom:10px; font-weight: 700;">
        {text}
    </h2>
    """


def render_info_box(markdown_content: str) -> str:
    """
    Renderiza un cuadro de información general con estilo institucional.

    Args:
        markdown_content (str): Texto en Markdown.

    Returns:
        str: HTML renderizado con diseño institucional.
    """
    html_content = md.markdown(markdown_content, extensions=['markdown.extensions.extra'])
    return f"""
    <div style="background-color:#F1F3F4; padding:15px; border-radius:10px; font-size:15px; line-height:1.5;">
        {html_content}
    </div>
    """


def render_data_protection_box(markdown_content: str) -> str:
    """
    Renderiza un cuadro de protección de datos o notas legales.

    Args:
        markdown_content (str): Texto en Markdown.

    Returns:
        str: HTML renderizado con diseño institucional.
    """
    html_content = md.markdown(markdown_content, extensions=['markdown.extensions.extra'])
    return f"""
    <div style="background-color:#E8F0FE; padding:15px; border-radius:8px; font-size:13px; line-height:1.4; border:1px solid #0073E6;">
        {html_content}
    </div>
    """


def render_compact_example_box(markdown_content: str) -> str:
    """
    Renderiza un cuadro de ejemplo o recordatorio con diseño compacto.

    Args:
        markdown_content (str): Texto en Markdown.

    Returns:
        str: HTML renderizado con diseño compacto.
    """
    html_content = md.markdown(markdown_content, extensions=['markdown.extensions.extra'])
    return f"""
    <div style="background-color:#FAFAFA; border-left:4px solid #0073E6; padding:8px 12px; border-radius:6px; font-size:13px; line-height:1.4;">
        {html_content}
    </div>
    """

def render_box(content):
    return f"""
    <div style='padding: 0.5rem; border: 1px solid #CCC; border-radius: 5px; background-color: #f9f9f9'>
    {content}
    </div>
    """ 

