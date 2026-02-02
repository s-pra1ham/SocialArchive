import os

# Get the terminal width
cols = os.get_terminal_size().columns

# Print a line of dashes spanning the full width
print('=' * cols)   

print(" " * ((cols - len("Downloading Reel ingestion")) // 2) + "Downloading Reel ingestion")