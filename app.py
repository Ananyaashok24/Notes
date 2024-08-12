from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# MongoDB Connection
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['notes_database']  # Replace 'notes_database' with your actual database name
    notes_collection = db['notes']
    client.admin.command('ping')  # Check if server is available
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        try:
            # Retrieve form data
            title = request.form.get('title')
            content = request.form.get('content')
            rating = request.form.get('rating')
            file = request.files['file']
            filename = file.filename if file else None

            # Validate form data (add your validation logic here)

            # Construct document
            document = {
                "title": title,
                "content": content,
                "rating": rating,
                "filename": filename
            }

            # Insert document into MongoDB
            notes_collection.insert_one(document)

            # Save file if it exists
            if file:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return "Note uploaded successfully!"
        except Exception as e:
            return str(e), 400

    return render_template('index.html')

@app.route('/view_notes', methods=['GET'])
def view_notes():
    notes = list(notes_collection.find())
    return render_template('upload.html', notes=notes)

@app.route('/rate_note', methods=['POST'])
def rate_note():
    try:
        note_id = request.form.get('note_id')
        new_rating = request.form.get('rating')

        # Update note rating in MongoDB
        notes_collection.update_one({'_id': ObjectId(note_id)}, {'$set': {'rating': new_rating}})

        return redirect(url_for('view_notes'))
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

