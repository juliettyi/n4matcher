from __future__ import absolute_import
from matcher import Matcher

m = Matcher('./1K/')
m.match_file('./test_imgs/chita.jpg', top_n=5)
