import re
import colorsys
from typing import Dict, Iterable

import pandas as pd
import numpy as np
from matplotlib.colors import to_rgb, to_hex

from st_dashboard.data.constants import AGG_MODEL_TYPES, FAMILY_RULES, FAMILY_BASE_COLORS


def classify_model_type(model_id: str, model_name: str) -> str:
    model_id = (model_id or "").lower()
    model_name = model_name or ""

    if "t2i" in model_id or "Text to Image" in model_name:
        return "t2i"
    if "i2i" in model_id or "Image to Image" in model_name:
        return "i2i"
    if "i2v" in model_id or "Image to Video" in model_name:
        return "i2v"
    if "v2v" in model_id or "Video to Video" in model_name:
        return "v2v"
    if "t2v" in model_id or "Text to Video" in model_name:
        return "t2v"
    if "t2s" in model_id or "Text to Speech" in model_name:
        return "t2s"
    if "s2v" in model_id or "Speech to Video" in model_name:
        return "s2v"
    if "Minimatics" in model_name:
        return "minimatics"
    if "Character Models" in model_name:
        return "character_models"
    if "Sound Effects" in model_name:
        return "sound_effects"
    return "unknown"


def _extract_from_inputs(inputs):
    """Extract model choice from modelConfig.inputs.

    Supports:
    - dict: {"tts_model": "eleven_v3", ...}
    - list of dicts: [{"id": "tts_model", "value": "eleven_v3", ...}, ...]
    """
    if isinstance(inputs, dict):
        for k, v in inputs.items():
            if str(k).lower() == "tts_model":
                return v
        for k, v in inputs.items():
            if "model" in str(k).lower():
                return v

    if isinstance(inputs, list):
        for item in inputs:
            if str(item.get("id", "")).lower() == "tts_model":
                return item.get("value") or item.get("defaultValue")
        for item in inputs:
            if "model" in str(item.get("id", "")).lower():
                return item.get("value") or item.get("defaultValue")

    return None


def _normalize_replicate_id(model_id: str, model_type: str):
    if not model_id:
        return None
    model_id = str(model_id)
    prefix = f"{model_type}-"
    return model_id[len(prefix):] if model_id.startswith(prefix) else model_id


def extract_model_title(row: pd.Series) -> str:
    model_type = row.get("model_type")
    provider = str(row.get("modelConfig.provider", "")).upper()

    if model_type == "t2s":
        val = _extract_from_inputs(row.get("modelConfig.inputs"))
        return val or "unknown_t2s_model"

    if model_type == "i2i":
        if provider == "OPENAI":
            return row.get("modelConfig.modelMetaData.openAIModelId") or "unknown_openai_model"
        if provider == "REPLICATE":
            model_id = row.get("modelConfig.id")
            return _normalize_replicate_id(model_id, model_type) or "unknown_replicate_model"

    return row.get("modelConfig.modelTitle")


def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    created = pd.to_datetime(df.get("createdAt"), errors="coerce", utc=True)
    df["created_at"] = created
    df["dt"] = created.dt.strftime("%Y-%m-%d")
    iso = created.dt.isocalendar()
    df["isoyear"] = iso["year"]
    df["isoweek"] = iso.apply(lambda x: f"{x['year']}{x['week']:02d}", axis=1)
    df["week_start"] = created.dt.to_period("W").dt.start_time
    return df


def add_model_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["model_type"] = df.apply(
        lambda row: classify_model_type(row.get("modelConfig.id"), row.get("modelConfig.name")),
        axis=1,
    )
    df["model_type_agg"] = df["model_type"].apply(
        lambda x: x if x in AGG_MODEL_TYPES else "other"
    )
    df["model_title_extracted"] = df.apply(extract_model_title, axis=1)
    return df


def add_quality_and_cost(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["default_cost"] = pd.to_numeric(
        df.get("modelConfig.costConfig.defaultCost"), errors="coerce"
    )
    df["quality_score"] = pd.to_numeric(
        df.get("qualityAnalysis.score"), errors="coerce"
    )
    if "resultDownloadedAt" in df.columns:
        df["was_downloaded"] = df["resultDownloadedAt"].notna()
    else:
        df["was_downloaded"] = False
    if "qualityAnalysis.rewrittenPrompt" in df.columns:
        df["has_rewrite"] = df["qualityAnalysis.rewrittenPrompt"].notna() & (
            df["qualityAnalysis.rewrittenPrompt"].astype(str).str.len() > 0
        )
    else:
        df["has_rewrite"] = False
    return df


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = add_time_columns(df)
    df = add_model_columns(df)
    df = add_quality_and_cost(df)
    return df


def detect_family(title: str) -> str:
    if not title:
        return "other"
    s = str(title).lower()
    for fam, pattern in FAMILY_RULES:
        if re.search(pattern, s):
            return fam
    return "other"


def ramp_around_base(base_hex: str, n: int, light_shift: float = 0.22, dark_shift: float = 0.18):
    if n <= 1:
        return [base_hex]

    h, l, s = colorsys.rgb_to_hls(*to_rgb(base_hex))
    l_light = min(l + light_shift, 0.85)
    l_dark = max(l - dark_shift, 0.15)
    levels = list(np.linspace(l_light, l_dark, n))

    # Force a level to equal base lightness
    idx = int(min(range(n), key=lambda i: abs(levels[i] - l)))
    levels[idx] = l

    return [to_hex(colorsys.hls_to_rgb(h, li, s)) for li in levels]


def build_family_palette(titles: Iterable[str], totals: Dict[str, float] = None) -> Dict[str, str]:
    family_map = {}
    for t in titles:
        family_map.setdefault(detect_family(t), []).append(t)

    palette = {}
    for fam, items in family_map.items():
        base = FAMILY_BASE_COLORS.get(fam, FAMILY_BASE_COLORS["other"])
        if totals is not None:
            items = sorted(items, key=lambda x: totals.get(x, 0), reverse=True)
        else:
            items = sorted(items)
        shades = ramp_around_base(base, len(items))
        for t, c in zip(items, shades):
            palette[t] = c
    return palette
