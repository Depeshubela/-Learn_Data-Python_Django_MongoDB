import pymongo
from catalog.models import BookInstance

myclient = pymongo.MongoClient("mongodb+srv://sean940106:joy50923@cluster0.jn3cu9l.mongodb.net/test")
mydb = myclient["test"]
mycol = mydb["catalog_bookinstance"]

print(BookInstance.objects.filter(status__exact="o").order_by('due_back')
)
for x in mycol.find({},{ "_id": 0,}):
  print(x)