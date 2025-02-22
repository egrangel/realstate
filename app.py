from flask import Flask, flash, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'thisisthesecretkey'

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            util_area REAL,
            num_rooms INTEGER,
            price REAL,
            num_garage INTEGER,
            num_bathroom INTEGER,
            image TEXT,
            date_created TEXT
          )
              ''')
    conn.commit()
    conn.close()

init_db()

# Home page - List all properties
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, description, util_area, num_rooms, price, num_garage, num_bathroom, image, date_created FROM properties')
    properties = c.fetchall()
    conn.close()
    return render_template('index.html', properties=properties)

# Property detail page
@app.route('/property/<int:id>')
def property_detail(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, description, util_area, num_rooms, price, num_garage, num_bathroom, image, date_created FROM properties WHERE id = ?', (id,))
    property = c.fetchone()
    conn.close()
    if property:
        return render_template('property_detail.html', property=property)
    return 'Property not found', 404

# Add new property
@app.route('/property/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        description = request.form['description']
        util_area = request.form['util_area']
        num_rooms = request.form['num_rooms']
        price = request.form['price']
        num_garage = request.form['num_garage']
        num_bathroom = request.form['num_bathroom']
        image = []
        
        # Save uploades images
        for file in request.files.getlist('images'):
            if file.filename != '':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(image_path)
                image.append(file.filename)

        # Save property to database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO properties (description, util_area, num_rooms, price, num_garage, num_bathroom, image, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (description, util_area, num_rooms, price, num_garage, num_bathroom, ','.join(image)))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_property.html')

# Delete property
@app.route('/property/delete/<int:id>', methods=['POST'])
def delete_property(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Fetch property to get the image filenames
    c.execute('SELECT image FROM properties WHERE id = ?', (id,))
    property = c.fetchone()

    if property:
        # Delete associated images from the filesystem
        for image in property[0].split(','):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
            if os.path.exists(image_path):
                os.remove(image_path)

        c.execute('DELETE FROM properties WHERE id = ?', (id,))
        conn.commit()

        flash('Property deleted successfully', 'success')
    else:
        flash('Property not found', 'error')

    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
