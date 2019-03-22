from notion.client import NotionClient
import json

def init():
    with open('./config.json') as config_file:
        config = json.load(config_file)
        client = NotionClient(token_v2=config['token_v2'])
        return client, client.get_collection_view("https://www.notion.so/mdnt/25a979d31e6045118104bd2a6ea1355c?v=7b8ae192dc424628ab5362ba0dc02929")

def main():
    client, root_page = init()
    print(root_page)


if __name__ == "__main__":
    main()