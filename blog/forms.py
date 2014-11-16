from django import forms
from applib.mptt.forms import TreeNodeChoiceField
from blog.models import Entry, Category


class EntryForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all())
    tags = forms.CharField(required=False)

    class Meta:
        model = Entry
        fields = ('title', 'content', 'hidden', 'image', 'category')

    def clean_tags(self):
        return self.cleaned_data['tags'].replace(' ', '')

    def save(self, user):
        entry = super(EntryForm, self).save(commit=False)
        entry.user = user
        entry.save()
        entry.save_entry_tags(self.cleaned_data['tags'])
        return entry