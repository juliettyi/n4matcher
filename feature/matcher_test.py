from matcher import Matcher

m = Matcher('./1K/')
m.match_file('./test_imgs/cat.jpg', top_n=5)
