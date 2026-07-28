import re

RISK_PATTERN = re.compile(
    r"risk of\s+(.*?)\s+can be",
    re.IGNORECASE
)

SERUM_PATTERN = re.compile(
    r"serum concentration of\s+(.*?)\s+can be",
    re.IGNORECASE
)

METABOLISM_PATTERN = re.compile(
    r"metabolism of\s+(.*?)\s+can be",
    re.IGNORECASE
)

EXCRETION_PATTERN = re.compile(
    r"excretion (?:rate )?of\s+(.*?)\s+can be",
    re.IGNORECASE
)

THERAPEUTIC_PATTERN = re.compile(
    r"therapeutic efficacy of\s+(.*?)\s+can be",
    re.IGNORECASE
)
