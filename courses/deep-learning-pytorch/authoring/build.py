import specs
from render import ROOT, SPECS, write_all
from depth_reviews import apply_reviews, write_review_matrix

apply_reviews(SPECS)
write_all()
write_review_matrix(ROOT)
