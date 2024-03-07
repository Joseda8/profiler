import time

# Initialize a variable i to 0
i = 0

# Create a list named containing many elements, all initialized to 0
my_list = [0] * (10**7)

# Loop while i is less than 2
while i < 2:
    # Double the size of the list by concatenating it with itself
    my_list += my_list
    
    # Modify each element of the list by raising it to the power of itself
    my_list = [(x ** x) for x in my_list]
    
    # Increment i by 1
    i += 1
    print(f"i: {i}")

    # Sleep
    time.sleep(0.5)
