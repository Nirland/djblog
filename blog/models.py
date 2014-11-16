from django.db import models, connection
from django.contrib.auth.models import User
from applib.mptt.models import MPTTModel
from applib.mptt.fields import TreeForeignKey
from applib.pytils.translit import slugify
from applib.thumbs import ImageWithThumbsField
import settings
import datetime


class Category(MPTTModel):
    title = models.CharField(max_length = 100, unique=True)
    slug = models.SlugField(max_length = 100)
    description = models.CharField(max_length = 255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    class MPTTMeta:
        level_attr = 'level'
        order_insertion_by = ['title',]

    class Meta:
        db_table = settings.DB_TABLE_CATEGORY_FULL
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('cat_view', [], {'category': self.slug})


class TagManager(models.Manager):
    def get_tags_cloud(self):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT DISTINCT tag.name, tag.slug, COUNT(tag.name) as count
                       FROM %(tag_tbl)s as tag
                       JOIN %(entrytag_tbl)s as etag ON (tag.id = etag.%(tag)s_id)
                       JOIN %(entry_tbl)s as entry ON (etag.%(entry)s_id = entry.id)
                       GROUP BY tag.name, tag.slug
                       ORDER BY count DESC
					   LIMIT %(max_tags)s
                       """ % {'tag_tbl': settings.DB_TABLE_TAG_FULL,
                              'entrytag_tbl': settings.DB_TABLE_ENTRYTAG_FULL,
                              'entry_tbl': settings.DB_TABLE_ENTRY_FULL,
                              'tag': settings.DB_TABLE_TAG,
                              'entry': settings.DB_TABLE_ENTRY,
							  'max_tags': settings.MAX_TAGS}
        )
        rows = cursor.fetchall()
        if not rows:
            return []
        rows = sorted(rows, key = lambda row: row[0])
        min_count = max_count = rows[0][2]
        tags = []
        for tag_name, tag_slug, tag_count in rows:
            tags.append({'name': tag_name, 'slug': tag_slug, 'weight': tag_count})
            if tag_count < min_count:
                min_count = tag_count
            if max_count < tag_count:
                max_count = tag_count
        range = float(max_count - min_count)
        if range == 0.0:
            range = 1.0
        for tag in tags:
            tag['weight'] = int(settings.MAX_WEIGHT * (tag['weight'] - min_count) / range)
        return tags

class Tag(models.Model):
    name = models.CharField(max_length = 100, unique=True)
    slug = models.SlugField(max_length = 100)

    objects = TagManager()

    class Meta:
        db_table = settings.DB_TABLE_TAG_FULL
        ordering = ['name']
        verbose_name_plural = "Tags"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
       return ('tag_view', [], {'tag': self.slug})


class EntryManager(models.Manager):
    def get_archives(self):
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT DATE_FORMAT(entry.pub_date, '%%%%m %%%%Y') as archive, COUNT(entry.pub_date)
                       FROM %(entry_tbl)s as entry
                       GROUP BY archive
                       ORDER BY archive DESC
                       """ % {'entry_tbl': settings.DB_TABLE_ENTRY_FULL})
        rows = cursor.fetchall()
        archives = []
        for archive, entry_count in rows:
            archives.append({'name': datetime.datetime.strptime(archive, "%m %Y"), 'entry_count': entry_count})
        return archives

class Entry(models.Model):
    title = models.CharField(max_length = 250)
    slug = models.SlugField(max_length = 250, unique_for_date='pub_date', db_index = True)
    content = models.TextField()
    hidden = models.BooleanField()
    pub_date = models.DateTimeField()
    image = ImageWithThumbsField(upload_to='upload', null=True, blank=True, sizes=((100,100),(400,300)))
    category = TreeForeignKey(Category, related_name='entries')
    user = models.ForeignKey(User, related_name='entries')
    tags = models.ManyToManyField(Tag, null=True, blank=True, related_name='entries', db_table=settings.DB_TABLE_ENTRYTAG_FULL)

    objects = EntryManager()

    class Meta:
        db_table = settings.DB_TABLE_ENTRY_FULL
        ordering = ['-pub_date']
        verbose_name_plural = "Entries"

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.pub_date = datetime.datetime.now()
        self.slug = slugify(self.title)

        if self.id:
            last_instance = Entry.objects.get(id=self.id)
        else:
            last_instance = None
        super(Entry, self).save(*args, **kwargs)
        if (last_instance and self.image) and (last_instance.image.path != self.image.path):
            last_instance.image.delete()

    def delete(self):
        if self.image:
            self.image.delete()
        super(Entry, self).delete()

    @models.permalink
    def get_absolute_url(self):
         return ('entry_detail', [], {'year': self.pub_date.strftime("%Y"),
                                      'month': self.pub_date.strftime("%m"),
                                      'day': self.pub_date.strftime("%d"),
                                      'slug': self.slug })

    def save_entry_tags(self, raw_tags):
         tags = raw_tags.split(settings.TAG_DELIMITER)
         tag_objects = []
         for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            tag_objects.append(tag_obj)
         self.tags = tag_objects
         self.save()