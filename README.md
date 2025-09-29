# Elasticsearch Index Migration Tool

This tool helps you **migrate data from one Elasticsearch index to another** with support for:
- Custom **index mappings**,
- Source and destination **Elasticsearch credentials**,
- Configurable **batch size** for bulk migration.

It is useful when you need to move data between clusters or reindex with a new mapping.

---

## Features
- Reads **source and destination Elasticsearch configs** from `config.yaml`.
- Uses a custom mapping defined in `mapping.json`.
- Automatically creates the destination index if it doesn’t exist.
- Migrates documents in batches using the Elasticsearch `helpers.bulk` API.
- Preserves document `_id` and also adds it to the document body as `id`.

---

## Requirements
- Python 3.8+
- Elasticsearch 8.x Python client

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Configuration

### `config.yaml`
Define your source and destination Elasticsearch connections:

```yaml
src:
  conn_str: "http://localhost:9200"
  index: "source_index"
  username: "elastic"
  password: "your_password"

dst:
  conn_str: "http://localhost:9200"
  index: "destination_index"
  username: "elastic"
  password: "your_password"

batch_size: 500
```

### `mapping.json`
Define the mapping for the destination index, e.g.:

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": { "type": "text" },
      "timestamp": { "type": "date" }
    }
  }
}
```

---

## Usage

Run the migration:
```bash
python migrate.py
```

The script will:
1. Connect to source and destination Elasticsearch clusters.
2. Create the destination index if it doesn’t exist.
3. Migrate data from the source index in batches.

---

## Logging

The script outputs informative logs:
```text
2025-08-28 14:00:00 :: Elastic search parser :: INFO     :: Initialization..
2025-08-28 14:00:00 :: Elastic search parser :: INFO     :: Connect to elasticsearch..
2025-08-28 14:00:01 :: Elastic search parser :: INFO     :: Create a new index (if it doesn't exist)..
2025-08-28 14:00:01 :: Elastic search parser :: INFO     :: Migrate data to new index, please wait..
2025-08-28 14:00:05 :: Elastic search parser :: INFO     :: Success.
```

---

## Notes
- Make sure your Elasticsearch instances are accessible from the machine running the script.
- If authentication is not required, leave `username` and `password` empty in the `config.yaml`.
- Batch size can be tuned depending on your dataset and cluster performance.

---

## License
MIT License
