import shelve

# Does NOT Support Concurrent Read/Write Access
d = shelve.open("datasource")
#d = shelve.open(datasource,writeback=True)
    # Allows for d['x'].append("")
    # ! Consumes more memory
    # ! d.close() is slower

try :
    print d["derp.txt"]
except KeyError :
    print "Does Not Exist"


d["merp.txt"] = "Merp"
d["derp.txt"] = "Derp"

# KeyError if DNE
print d["merp.txt"]

#flag = d.has_key(key) #(True) if key exists

d.close()
