APP_NAME = 'blog'

DB_TABLE_CATEGORY = 'category'
DB_TABLE_TAG = 'tag'
DB_TABLE_ENTRY = 'entry'
DB_TABLE_ENTRYTAG = 'entry_tag'
DB_TABLE_COMMENT = 'comment'

DB_TABLE_CATEGORY_FULL = APP_NAME + '_' + DB_TABLE_CATEGORY
DB_TABLE_TAG_FULL = APP_NAME + '_' + DB_TABLE_TAG
DB_TABLE_ENTRY_FULL = APP_NAME + '_' + DB_TABLE_ENTRY
DB_TABLE_COMMENT_FULL = APP_NAME + '_' + DB_TABLE_COMMENT
DB_TABLE_ENTRYTAG_FULL = APP_NAME + '_' + DB_TABLE_ENTRYTAG

#tags
MAX_WEIGHT = 5
MAX_TAGS = 20
TAG_DELIMITER = ','

#blog
ENTRIES_PER_PAGE = 10
FRESH_ENTRIES_COUNT = 5
RELATED_ENTRIES_COUNT = 5