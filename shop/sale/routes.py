from flask_login import current_user
from shop import app, db
from shop.decorators import role_required
from flask import render_template, redirect, url_for, flash
from shop.customers.model import Order, Customer
from shop.products.models import AddProduct

@app.route('/sales')
@role_required(['sale'])
def sales():
    products = AddProduct.query.all()
    return render_template('sale/sales.html', title='Sales Dashboard', products=products)

@app.route('/manager_orders', methods=['GET', 'POST'])
@role_required(['admin', 'sale'])
def manager_order():
    orders = Order.query.all()
    return render_template('sale/manager_orders.html', title='Orders Page', orders=orders)

@app.route('/order_detail/<int:id>')
@role_required(['admin', 'sale'])
def order_detail(id):
    order = Order.query.get_or_404(id)
    order_details = order.order_details
    grand_total = 0
    sub_total = 0
    tax = 0

    # Calculate totals based on order details
    for item in order_details:
        # Calculate item price with discount
        discount_amount = (item.discount / 100) * float(item.price) if hasattr(item, 'discount') else 0
        item_price = float(item.price) - discount_amount
        item_total = item_price * int(item.quantity)
        sub_total += item_total
    # Calculate tax and grand total
    tax = float("%.2f" % (.06 * sub_total))
    grand_total = float("%.2f" % (1.06 * sub_total))

    return render_template('sale/order_detail.html', grand_total=grand_total, tax=tax, order=order, order_details=order_details, title='Order Detail')

@app.route('/accept_order/<int:id>', methods=['POST'])
@role_required(['admin', 'sale'])
def accept_order(id):
    if current_user.is_authenticated:
        order = Order.query.get_or_404(id)
        order.staff_id = current_user.id
        order.status = 'accepted'
        db.session.commit()
        flash('Order status changed successfully', 'success')
        return redirect(url_for('manager_order'))
    else:
        flash('You need to be logged in to change order status', 'danger')
        return redirect(url_for('login'))

@app.route('/complete_order/<int:id>', methods=['POST'])
@role_required(['admin', 'sale'])
def complete_order(id):
    if current_user.is_authenticated:
        order = Order.query.get_or_404(id)
        order.status = 'completed'
        order.is_completed = True
        order.staff_id = current_user.id
        db.session.commit()
        flash('Order completed successfully', 'success')
        return redirect(url_for('manager_order'))
    else:
        flash('You need to be logged in to complete an order', 'danger')
        return redirect(url_for('login'))