import yaml
import json
import logging
import warnings
from elasticsearch import Elasticsearch, helpers

warnings.filterwarnings(action="ignore")


class ElasticParser:
    def __init__(self):
        self.conf = ElasticParser.config()
        # Connection strings
        self.src_conn_str = self.conf["src"]["conn_str"]
        self.dst_conn_str = self.conf["dst"]["conn_str"]
        # Indexes
        self.src_index = self.conf["src"]["index"]
        self.dst_index = self.conf["dst"]["index"]
        # Usernames
        self.src_username = self.conf["src"]["username"]
        self.dst_username = self.conf["dst"]["username"]
        # Passwords
        self.src_password = self.conf["src"]["password"]
        self.dst_password = self.conf["dst"]["password"]
        # New Mapping
        self.new_mapping = ElasticParser.mapping()
        # Elasticsearch clients
        self.src_client = None
        self.dst_client = None

    def connect(self):
        if self.src_username and self.src_password:
            self.src_client = Elasticsearch(
                hosts=[self.src_conn_str],
                verify_certs=False,
                basic_auth=(self.src_username, self.src_password),
            )
        else:
            self.src_client = Elasticsearch(hosts=[self.src_conn_str], verify_certs=False)

        if self.dst_username and self.dst_password:
            self.dst_client = Elasticsearch(
                hosts=[self.dst_conn_str],
                verify_certs=False,
                basic_auth=(self.dst_username, self.dst_password),
            )
        else:
            self.dst_client = Elasticsearch(hosts=[self.dst_conn_str], verify_certs=False)

    def create_index(self):
        if not self.dst_client.indices.exists(index=self.dst_index):
            self.dst_client.indices.create(index=self.dst_index, body=self.new_mapping)

    def scan_index(self):
        return helpers.scan(
            self.src_client,
            index=self.src_index,
            query={"query": {"match_all": {}}},
        )

    def migrate(self):
        actions = []

        for doc in self.scan_index():
            doc["_source"]["id"] = doc["_id"]
            action = {"_index": self.dst_index, "_id": doc["_id"], "_source": doc["_source"]}
            actions.append(action)

            if len(action) == self.conf["batch_size"]:
                helpers.bulk(self.dst_client, actions)
                action.clear()

        if len(action):
            helpers.bulk(self.dst_client, actions)
            action.clear()

    @staticmethod
    def mapping() -> dict:
        with open("mapping.json", "r") as file:
            return json.load(file)

    @staticmethod
    def config() -> dict:
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s")
    logger = logging.getLogger("Elastic search parser")
    logger.info("Initialization..")
    parser = ElasticParser()
    logger.info("Connect to elasticsearch..")
    parser.connect()
    logger.info("Create a new index (if it doesn't exist)..")
    parser.create_index()
    logger.info("Migrate data to new index, please wait..")
    parser.migrate()
    logger.info("Success.")
