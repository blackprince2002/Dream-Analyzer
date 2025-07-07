import pandas as pd
import re

# Load the dataset
df = pd.read_csv('dreams.csv')

# Function to clean and preprocess the dream text
def preprocess_text(text):
    # Ensure the input is a string
    if isinstance(text, str):
        # Remove unwanted characters, extra spaces, and line breaks
        text = re.sub(r'\n|\r|\t', ' ', text)  # Remove newline and tab characters
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = text.strip()  # Remove leading and trailing spaces
    return text

# Apply preprocessing to each dream text
df['dreams_text'] = df['dreams_text'].apply(preprocess_text)

# Save the cleaned dataset to a new CSV file
df.to_csv('cleaned_dreams.csv', index=False)

print("Cleaned dreams saved to 'cleaned_dreams.csv'.")
