# freshcart-pipelines

Data Engineering assignment starter repository: Git/CI, Iris Mage pipeline, and RabbitMQ topic stream.

## Repository structure

```text
freshcart-pipelines/
├── README.md
├── .gitignore
├── requirements.txt
├── elt/                         # Add the instructor FreshCart notebook here
├── iris_project/                # Mage Iris pipeline blocks + metadata
├── stream/                      # RabbitMQ dispatcher and driver
├── tests/test_prepare_data.py
└── .github/workflows/ci.yml
```

## Local Python setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
```

The CI test runs without Mage because the block files use no-op decorator fallbacks when Mage is not installed. To run the orchestration portion, install Mage in a compatible Python environment and open this project in Mage; confirm/import the blocks and verify the generated pipeline metadata in the Mage UI. The provided `metadata.yaml` is a readable starting graph, and Mage versions may generate additional UUID/configuration fields.

## GitHub Actions

Create a GitHub repository named `freshcart-pipelines`, then connect and push this local repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/freshcart-pipelines.git
git push -u origin main
```

The workflow in `.github/workflows/ci.yml` runs pytest on every push. To demonstrate a red run, temporarily change `TEST_SIZE` in `iris_project/transformers/prepare_data.py` from `0.2` to `0.3`, commit and push, capture the failing Actions run, then restore `0.2`, commit and push again and capture the green run.

## Mage pipeline

Blocks: `load_iris` (data_loader) -> `validate_iris` (transformer) -> `prepare_data` (transformer) -> `train_model` (transformer) -> `save_results` (data_exporter), with `evaluate_model` (transformer) as a second branch from `train_model`.

Run the assignment's command from the Mage project environment after registering the pipeline:

```bash
mage run iris_project iris_classifier --test
```

Runtime variable example (exact CLI syntax can vary by Mage release):

```bash
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 3}'
```

The model test requires test accuracy >= 0.90. For the reproducible split in this repo, max_depth=1 fails; max_depth=2..5 pass. Delete `iris_predictions.csv` before each depth experiment.

## RabbitMQ stream

Install RabbitMQ and start the service. Install Python requirements, then open separate terminals:

```bash
python -m stream.driver Ravi 'bangalore.koramangala.*'
python -m stream.driver Priya 'bangalore.indiranagar.*'
python -m stream.driver Arjun 'bangalore.*.ride'
python -m stream.driver Meena 'bangalore.*.food'
python -m stream.dispatcher --interval 2 --duration 120 --bad-every 10
```

For D1 deterministic routing-key evidence, start the drivers and run:

```bash
python -m stream.send_demo
```

Set `RABBITMQ_URL` as an environment variable when using a hosted broker. Never put the broker URL/password in Git. The dispatcher omits the `zone` field from every tenth message while retaining a routing key, allowing drivers to NACK malformed messages. The driver uses `basic_ack` for valid messages and `basic_nack(requeue=False)` for missing-zone/invalid-JSON messages.

## Snowflake ELT

Add the instructor's FreshCart notebook under `elt/` and run it with your own Snowflake account. The assignment PDF contains expected baseline outputs but not the notebook's exact SQL, table DDL, field names, or mock source rows; use the provided notebook as the source of truth for Parts B2-B5. Do not put Snowflake credentials in this repository.
