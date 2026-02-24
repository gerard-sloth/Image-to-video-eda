# Studio Jadu Monitoring Dashboard

This repo contains a Streamlit dashboard for monitoring Studio Jadu's AI generation usage across text-to-image, image-to-image, image-to-video, and related tasks. The dashboard reads from MongoDB, applies the same transformations used in the exploratory notebook, and presents two views:

- **Overview** — high-level trends over time (job volume and cost), broken down by task type.
- **Task Breakdown** — a deep dive into a specific task (e.g., i2i), with model-level usage, cost, and quality signals.

## What the dashboard shows

**Overview tab**
- Requests over time (absolute or percent) by task type
- Cost over time (absolute or percent) by task type
- Jobs + total cost per task type (grouped bars)

**Task Breakdown tab**
- Usage and cost trends by model title
- Quality distributions + download rates
- Average cost per model and weekly cost trends
- Quality vs. cost scatterplots

## Run the dashboard

From the repo root:

```bash
uv run streamlit run "st_dashboard/🔎_Overview.py"
```

If you renamed the file, run the new path instead (the sidebar label comes from the filename).

## Configuration

The app connects to MongoDB using environment variables in `.env`:

```
MONGO_USER=...
MONGO_PASSWORD=...
MONGO_HOST=...
```

These are read by `config/settings.py` and used in `src/mongo/mongo_db_client.py`.

## Optional: install uv

If you don’t have `uv` installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your shell after installation.

## Sync dependencies with uv

After pulling the repo or updating dependencies:

```bash
uv sync
```

Then run the dashboard:

```bash
uv run streamlit run "st_dashboard/🔎_Overview.py"
```

## Project layout

```
st_dashboard/
  🔎_Overview.py              # main page (Overview tab)
  pages/
    🧩_Task_Breakdown.py       # Task Breakdown tab
  data/
    loader.py                 # MongoDB load + caching
    transforms.py             # data transformations (model_type, isoweek, cost, quality, etc.)
    constants.py              # model families + palettes
  charts/
    overview.py               # overview charts (Plotly)
    task_breakdown.py         # task charts (Plotly + Matplotlib)
  theme/
    style.css                 # light UI styling
  assets/
    studio-jadu.png           # logo
```

## Notes

- The dashboard caches data for 15 minutes to keep the UI responsive.
- If quality scores are missing for a task type (e.g., t2s), the quality plots are skipped with a friendly message.
- The sidebar filters control date range, task selection, and plot mode.

## Troubleshooting

**Streamlit not found**

```bash
uv add streamlit plotly
uv sync
```

**Mongo connection errors**
- Check `.env` values and network access.
- The Mongo client uses timeouts to avoid hanging.

---

If you want additional filters, visual tweaks, or new metrics, open an issue or ping me.
