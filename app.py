import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from config import Config
from models import db, Product, Order

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    products = Product.query.filter_by(is_new=True).limit(4).all()
    return render_template('index.html', products=products)

@app.route('/catalog')
def catalog():
    category = request.args.get('category', 'all')
    if category == 'all':
        products = Product.query.all()
    else:
        products = Product.query.filter_by(category=category).all()
    return render_template('catalog.html', products=products, current_category=category)

@app.route('/product/<slug>')
def product(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template('product.html', product=product)

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/delivery')
def delivery():
    return render_template('delivery.html')

@app.route('/admin')
def admin_dashboard():
    products = Product.query.all()
    orders = Order.query.all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_product_new():
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        price = int(request.form['price'])
        price_usd = int(price / 90)
        category = request.form['category']
        color = request.form['color']
        material = request.form['material']
        description = request.form['description']

        image_file = request.files['image']
        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        product = Product(
            name=name,
            slug=slug,
            price=price,
            price_usd=price_usd,
            category=category,
            color=color,
            material=material,
            description=description,
            image=filename
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_product_edit(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.slug = request.form['slug']
        product.price = int(request.form['price'])
        product.price_usd = int(product.price / 90)
        product.category = request.form['category']
        product.color = request.form['color']
        product.material = request.form['material']
        product.description = request.form['description']

        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=product)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def admin_product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ===== ОПЛАТА =====
@app.route('/create-crypto-payment', methods=['POST'])
def create_crypto_payment():
    data = request.json
    product = Product.query.get(data['product_id'])
    return jsonify({
        'success': True,
        'address': 'ТВОЙ_АДРЕС_PHANTOM',
        'amount': product.price_usd,
        'currency': 'USDT'
    })

@app.route('/create-card-payment', methods=['POST'])
def create_card_payment():
    data = request.json
    product = Product.query.get(data['product_id'])
    return jsonify({
        'success': True,
        'checkout_url': f'https://crossmint.com/checkout/{product.id}'
    })

@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all()
        return '✅ База данных создана! Эту страницу можно удалить.'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
