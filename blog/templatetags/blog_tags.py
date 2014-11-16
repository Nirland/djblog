from django.template import Library
from django.db import models
from blog.models import Category, Tag, Entry
from blog import settings
import re

register = Library()

@register.inclusion_tag('entry_cut.html', takes_context=True)
def entry_cut(context):
    content = context['entry'].content
    link_text = ''
    show_link = False
    pattern = re.compile(r'\[more[ ]*(?P<text>[ \w]*)[ ]*\].+\[/more\]', re.U|re.DOTALL)
    matches = pattern.search(content)
    if matches:
        if matches.group('text'):
            link_text = matches.group('text')
        content = pattern.sub('', content)
        show_link = True
    return {'content': content,
            'link_url':  context['entry'].get_absolute_url(),
            'link_text': link_text,
            'show_link': show_link}

@register.filter
def get_cut(content):
    pattern = re.compile(r'\[more[ ]*[ \w]*[ ]*\]', re.U)
    content = pattern.sub('<a name="cut">', content)
    content = content.replace(ur'[/more]', '</a>')
    return content

@register.inclusion_tag('categories.html')
def categories_tree():
    return {'categories': Category.tree.annotate(num_entries=models.Count('entries'))}

@register.inclusion_tag('tags.html')
def tags_cloud():
    return {'tags': Tag.objects.get_tags_cloud()}

@register.inclusion_tag('archives.html')
def archive_months():
    return {'archives': Entry.objects.get_archives()}

@register.inclusion_tag('entries_fresh.html')
def fresh_entries():
    return {'fresh_entries': Entry.objects.all()[:settings.FRESH_ENTRIES_COUNT]}