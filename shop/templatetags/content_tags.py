import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter
def render_content(text, content_images):
    """Replace [img:N] tags with actual images, then apply linebreaks."""
    text = escape(text)

    image_map = {}
    if content_images:
        for img in content_images:
            image_map[img.number] = img.image.url

    def replace_tag(match):
        num = int(match.group(1))
        url = image_map.get(num)
        if url:
            return (
                f'</p>'
                f'<figure class="my-8">'
                f'<img src="{url}" alt="" class="w-full rounded-lg shadow-md">'
                f'</figure>'
                f'<p>'
            )
        return match.group(0)

    text = re.sub(r'\[img:(\d+)\]', replace_tag, text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    result = '\n'.join(f'<p class="mb-4">{p.replace(chr(10), "<br>")}</p>' for p in paragraphs)
    return mark_safe(result)
