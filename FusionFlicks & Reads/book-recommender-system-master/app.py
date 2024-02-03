from flask import Flask, render_template, request
import pickle
import numpy as np
import os

app = Flask(__name__)

# Get the absolute path to the directory containing the Flask app
base_dir = os.path.abspath(os.path.dirname(__file__))

# Load the pickle files using the absolute path
popular_df = pickle.load(open(os.path.join(base_dir, 'popular.pkl'), 'rb'))
pt = pickle.load(open(os.path.join(base_dir, 'pt.pkl'), 'rb'))
books = pickle.load(open(os.path.join(base_dir, 'books.pkl'), 'rb'))
similarity_scores = pickle.load(open(os.path.join(base_dir, 'similarity_scores.pkl'), 'rb'))

@app.route('/')
def index():
    # Assuming popular_df contains the top 20 books
    top_20_books_df = popular_df.head(18)

    return render_template('index.html',
                           book_names=list(top_20_books_df['Book-Title'].values),
                           authors=list(top_20_books_df['Book-Author'].values),
                           images=list(top_20_books_df['Image-URL-M'].values),
                           votes=list(top_20_books_df['num_ratings'].values),
                           ratings=list(top_20_books_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Check if the user entered something
    if not user_input:
        return render_template('recommend.html', error="Please enter a book title")

    # Check if the user entered a valid title
    if user_input not in pt.index:
        return render_template('recommend.html', error="Book title not found in the dataset")

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:10]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
