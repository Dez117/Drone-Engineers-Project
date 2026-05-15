import datetime

# Convert Epoch time into something humans can actually understand
def whenis(epoch):
    time = datetime.datetime.fromtimestamp(epoch)
    formatted = time.strftime("%A, %B %d, %Y at %I:%M:%S %p")
    print(formatted)

# Print time stamps for all the log files
epochs = [
    #1747730280,2025
    #1778241292, nothing happens
    #1747760693, 2025
    1778241869,
    #1778229431, morning
    #1747729914, 2025
    #1778241642, nothing happens
    #1778227135, morning
    #1778241623, nothing happens
    1778239915,
    #1747758608, 2025
    #1778240668, nothing happens
    #1778239682, nothing happens
    #1747729189 2025
]

file_number = 0
for epoch in epochs:
    file_number += 1
    print("log file number", file_number)
    whenis(epoch)