import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--markdown-only", action="store_true")
arguments = parser.parse_args()

import specs
from render import ROOT, SPECS, write_all
from depth_reviews import apply_reviews, write_review_matrix

apply_reviews(SPECS)
write_all(markdown_only=arguments.markdown_only)
if not arguments.markdown_only:
    write_review_matrix(ROOT)
