from notion.client import NotionClient
from notion.markdown import notion_to_markdown
import notion
import os, sys, errno
import asyncio
import json
from datetime import date

def init():
    with open('./config.json') as config_file:
        config = json.load(config_file)
        client = NotionClient(token_v2=config['token_v2'])
        return (
            client,
            client.get_collection_view(config['sync_root']),
            config['destination']
        )


def silent_rm(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def get_markdown_from_page(block):
    print('traverse', block)
    if type(block) is notion.collection.CollectionRowBlock:
        return (
            block.get_property('title') + '\n\n' +
            '\n\n'.join([
                get_markdown_from_page(child)
                for child in block.children
            ])
        )
    elif type(block) is notion.block.TextBlock:
        return block.title
    elif type(block) is notion.block.HeaderBlock:
        return '# ' + block.title
    elif type(block) is notion.block.SubheaderBlock:
        return '## ' + block.title
    elif block.type == 'sub_sub_header':
        return '### ' + notion_to_markdown(block._get_record_data()['properties']['title'])
    elif type(block) is notion.block.BulletedListBlock:
        row = '- ' + block.title
        subrows = ''.join([
            '  ' + get_markdown_from_page(child)
            for child in block.children
        ])
        return row + '\n' + subrows
    elif type(block) is notion.block.NumberedListBlock:
        row = '1. ' + block.title
        subrows = ''.join([
            '  ' + get_markdown_from_page(child)
            for child in block.children
        ])
        return row + '\n' + subrows
    elif type(block) is notion.block.ColumnListBlock:
        subsections = '\n'.join([
            get_markdown_from_page(child)
            for child in block.children
        ])
        return '<section style="display:flex;">\n%s\n</section>' % subsections
    elif type(block) is notion.block.ColumnBlock:
        return '<section style="flex: %s">\n%s\n</section>' % (
            block.column_ratio,
            '\n'.join(get_markdown_from_page(child) for child in block.children)
        )
    elif type(block) is notion.block.ImageBlock:
        raw_source = notion_to_markdown(block._get_record_data()['properties']['source'])
        return '![%s](%s)' % (
            os.path.basename(raw_source),
            block.source
        )
    else:
        print(type(block), block, block._get_record_data())
        return str(block)

class RowSync:
    def __init__(self, root_dir, row):
        self.root_dir = root_dir
        self.row = row

    def start(self):
        self.filename = self._get_sync_filename()
        self.callback_id = self.row.add_callback(self.update_file)
        self.update_file()

    def update_file(self):
        if (self.is_published):
            print('row updated, writing file', self.filename)
            with open(self.filename, 'w') as file_handle:
                file_handle.write(get_markdown_from_page(self.row))
        else:
            silent_rm(self.filename)

    def remove_and_stop(self):
        self.row.remove_callbacks(self.callback_id)
        silent_rm(self.filename)

    def _get_sync_filename(self):
        # TODO format based on date of the entry
        return "%s/%s.md" % (self.root_dir, self.row.id)

    @property
    def is_published(self):
        is_published_status = any([
            self.row.get_property(entry['id']) == 'Published' for entry in self.row.schema if entry['name'] == "Status"
        ])

        publish_dates = [
            self.row.get_property(entry['id'])
                for entry in self.row.schema
                if (entry['name'] == "Publish Date"
                    and entry['type'] == 'date')
        ]
        dates = [publish_date.start for publish_date in publish_dates if publish_date is not None];
        is_published_date = len(dates) != 0 and max(dates) <= date.today()

        return is_published_status and is_published_date

class CollectionFileSync:
    def __init__(self, collection_view, root_dir):
        self.collection_view = collection_view
        self.root_dir = root_dir

        self.known_rows = dict()

    def start(self):
        self.callback = self.collection_view.add_callback(self.sync_rows)
        self.sync_rows()

    def stop(self):
        self.collection_view.add_callback(self.sync_rows)
        self.sync_rows()

    def sync_rows(self):
        print('syncing rows!')
        rows = self.collection_view.get_rows()
        rows_dict = dict((row.id, row) for row in rows)
        new_row_ids = frozenset(row.id for row in rows)
        old_row_ids = self.known_rows.keys()

        added_row_ids = new_row_ids - old_row_ids
        removed_row_ids = old_row_ids - new_row_ids

        print ("    added", added_row_ids, "removed", removed_row_ids)
        
        for added_row_id in added_row_ids:
            row_sync = RowSync(self.root_dir, rows_dict[added_row_id]);
            self.known_rows[added_row_id] = row_sync
            row_sync.start()

        for removed_row_id in removed_row_ids:
            self.known_rows[removed_row_id].remove_and_stop()
            del self.known_rows[removed_row_id]

def get_md_from_page(page):
    return str(page)

async def main():
    print('reading config')
    client, root_view, destination_dir = init()
    print('making out file')
    os.makedirs(destination_dir, exist_ok=True)

    print('got root')
    sync = CollectionFileSync(root_view.collection, destination_dir)
    print('starting sync')
    sync.start()

    print('entering indefinite wait')
    while True:
        sys.stdout.flush()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())