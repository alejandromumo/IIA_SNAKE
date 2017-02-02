import cProfile, pstats, io
from start import *
pr = cProfile.Profile()
pr.enable()
main("--fps")
x = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=x).sort_stats(sortby)
ps.print_stats()
print(x.getvalue())
pr.disable()