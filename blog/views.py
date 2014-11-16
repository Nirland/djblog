from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from blog.models import Entry, Category
from blog.forms import EntryForm
from blog import settings


def render_entries(get_entries):
    def response(*args, **kwargs):
        entries = get_entries(*args, **kwargs)
        return render_to_response('entries.html', {'entries': _get_paginated_entries(args[0], entries)},
                                  context_instance = RequestContext(args[0]))
    return response


@render_entries
def index(request):
    return Entry.objects.all().select_related()

@render_entries
def entries_by_category(request, category):
    category = get_object_or_404(Category, slug=category)
    categories = []
    if (category.is_root_node()):
        categories = list(category.get_children())
    categories.append(category)
    return Entry.objects.filter(category__slug__in=[category.slug for category in categories]).select_related()

@render_entries
def entries_by_tag(request, tag):
    return Entry.objects.filter(tags__slug=tag).select_related()

@render_entries
def entries_by_year(request, year):
    return Entry.objects.filter(pub_date__year=year).select_related()

@render_entries
def entries_by_month(request, year, month):
    return Entry.objects.filter(pub_date__year=year, pub_date__month=month).select_related()

@render_entries
def entries_by_day(request, year, month, day):
    return Entry.objects.filter(pub_date__year=year, pub_date__month=month, pub_date__day=day).select_related()


def entry_detail(request, year, month, day, slug):
    entry = get_object_or_404(Entry, pub_date__year=year, pub_date__month=month, pub_date__day=day, slug=slug)
    category = entry.category
    categories = []
    if category.is_child_node():
        categories = list(category.get_ancestors())
    categories.append(category)
    tags = entry.tags.all()
    related_entries = Entry.objects.filter(tags__id__in=[tag.id for tag in tags]).exclude(id=entry.id).distinct().order_by('?')[:settings.RELATED_ENTRIES_COUNT]
    return render_to_response('entry_detail.html',
                              {'entry': entry, 'categories': categories, 'tags': tags, 'related_entries': related_entries},
                              context_instance = RequestContext(request))


@login_required
def entry_add(request):
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(request.user)
            if entry.id > 0:
                return HttpResponseRedirect(entry.get_absolute_url())
        else:
            form_to_template = form
    else:
        form_to_template = EntryForm()
    return render_to_response('entry_modify.html',{'form': form_to_template, 'edit': False},
                              context_instance = RequestContext(request))

@login_required
def entry_edit(request, id):
    entry = get_object_or_404(Entry, pk=id)
    if entry.user != request.user:
        return HttpResponseRedirect(entry.get_absolute_url())
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save(request.user)
            return HttpResponseRedirect(entry.get_absolute_url())
        else:
           form_to_template = form
    else:
        form_to_template = EntryForm(instance=entry, initial={'tags': ','.join([tag.name for tag in entry.tags.all()])})
    return render_to_response('entry_modify.html',{'form': form_to_template, 'edit': True},
                              context_instance = RequestContext(request))

@login_required
def entry_delete(request, id):
    entry = get_object_or_404(Entry, pk=id)
    if entry.user != request.user:
        return HttpResponseRedirect(entry.get_absolute_url())
    entry.delete()
    return HttpResponseRedirect('/')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def _get_paginated_entries(request, qs):
    paginator = Paginator(qs, settings.ENTRIES_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    return entries