"""Find cross-split duplicates, shared groups, and token-overlap candidates."""
import argparse
import hashlib
import json
from pathlib import Path
import math
import re
import sys
import unicodedata


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())

