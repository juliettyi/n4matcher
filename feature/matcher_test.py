from matcher import Matcher

m = Matcher('./')
m.match_file('./test_imgs/00002.png', top_n=2)
