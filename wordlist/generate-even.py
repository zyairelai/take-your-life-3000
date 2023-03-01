# create an empty list 
wordlist = [] 
 
# loop to generate numbers from 0000-9999 
for num in range(0, 10000): 
      
    # to get the numbers with 4 digit 
    number = str(num).zfill(4) 
      
    # to check last digit is even 
    if int(number[-1]) % 2 == 0: 
          
        # append all even numbers to the wordlist 
        wordlist.append(number) 
  
# open a file and write all the even numbers in it 
with open('wordlist.txt', 'w') as filehandle: 
    for listitem in wordlist: 
        filehandle.write('%s\n' % listitem)
