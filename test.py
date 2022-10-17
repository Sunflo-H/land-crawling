dict1 = {
    'hello' : 1, 
    'brother' : 2
}

file1 = open("Original.txt", "w") 

str1 = repr(dict1)
print(str1)
file1.write("dict1 = " + str1 + "\n")
file1.close()
 
# f = open('Original.txt', 'r')
# if f.mode=='r':
#     contents= f.read()