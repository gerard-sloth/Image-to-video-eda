MAIN_MODEL_TYPES = ["t2i", "i2i", "i2v", "v2v", "t2v", "t2s"]
AGG_MODEL_TYPES = ["t2i", "i2i", "i2v", "v2v", "t2v"]
DEFAULT_TOP_N = 8

# Family mapping for model title coloring
FAMILY_RULES = [
    ("nanobanana", r"nano\s*banana|nanobanan|nano-banana"),
    ("gpt-image", r"gpt[-_ ]?image[-_ ]?1|gptimage"),
    ("flux", r"flux"),
    ("imagen", r"imagen"),
    ("seedance", r"seedance"),
    ("kling", r"kling"),
    ("runway", r"runway"),
    ("veo", r"veo"),
    ("elevenlabs", r"eleven"),
]

FAMILY_BASE_COLORS = {
    "nanobanana": "#4E79A7",  # blue
    "gpt-image": "#F28E2B",   # orange
    "flux": "#59A14F",        # green
    "imagen": "#E15759",      # red
    "seedance": "#76B7B2",    # teal
    "kling": "#EDC948",       # yellow
    "runway": "#B07AA1",      # violet
    "veo": "#FF9DA7",         # pink
    "elevenlabs": "#9C755F",  # brown
    "other": "#BAB0AC",       # gray
}
