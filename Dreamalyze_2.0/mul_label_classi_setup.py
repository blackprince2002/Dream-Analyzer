import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

# Load your dataset
df = pd.read_csv('dreams_with_categories.csv')

# Handle missing values in the 'dreams_text' column
df['dreams_text'] = df['dreams_text'].fillna('')

# Convert the 'categories' column into a list of categories
df['categories'] = df['categories'].apply(lambda x: eval(x) if isinstance(x, str) else [])

# Create the multi-label binarizer
mlb = MultiLabelBinarizer()

# Binarize the labels (categories)
y = mlb.fit_transform(df['categories'])

# Vectorize the text data using TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X = vectorizer.fit_transform(df['dreams_text'])

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a MultiOutputClassifier with Logistic Regression
clf = MultiOutputClassifier(LogisticRegression(max_iter=1000))
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='micro')

print(f"Accuracy: {accuracy:.4f}")
print(f"F1 Score (Micro): {f1:.4f}")

# Save the fitted MultiLabelBinarizer and vectorizer for future use
import joblib
joblib.dump(mlb, 'mlb.joblib')
joblib.dump(vectorizer, 'vectorizer.joblib')
