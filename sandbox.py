import cProfile
import database

db = database.Database()

pr = cProfile.Profile()
pr.enable()
db.loadCommentBatch(0,0)
pr.disable()
# after your program ends
pr.print_stats(sort="tottime")