from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tax_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class TaxPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # paid/unpaid
    due_date = db.Column(db.String(50), nullable=False)

# Initialize database
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True

# Home route with filtering and pagination
@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 5

    # Filter logic
    selected_due_date = request.form.get('due_date') if request.method == 'POST' else None
    if selected_due_date:
        query = TaxPayment.query.filter_by(due_date=selected_due_date)
    else:
        query = TaxPayment.query

    # Fetch paginated records
    records = query.paginate(page=page, per_page=per_page)

    # Calculate summary
    total_amount = sum(record.amount for record in records.items)
    tax_rate = 0.06  # 6% tax rate
    tax_due = total_amount * tax_rate

    return render_template(
        'index.html',
        records=records,
        due_dates=due_dates,
        selected_due_date=selected_due_date,
        total_amount=total_amount,
        tax_rate=tax_rate,
        tax_due=tax_due
    )

# Add record route
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        try:
            company = request.form['company']
            amount = float(request.form['amount'])
            payment_date = request.form['payment_date'] or None
            status = request.form['status']
            due_date = request.form['due_date']

            # Validate required fields
            if not company or not amount or not due_date:
                raise ValueError("All fields except 'Payment Date' are required!")

            # Save to database
            new_record = TaxPayment(
                company=company,
                amount=amount,
                payment_date=payment_date,
                status=status,
                due_date=due_date
            )
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return render_template('add_record.html', error=str(e))

    # Generate dynamic due dates
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]
    return render_template('add_record.html', due_dates=due_dates)

# Edit record route
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    record = TaxPayment.query.get_or_404(id)

    if request.method == 'POST':
        try:
            record.company = request.form['company']
            record.amount = float(request.form['amount'])
            record.payment_date = request.form['payment_date'] or None
            record.status = request.form['status']
            record.due_date = request.form['due_date']

            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return render_template('edit_record.html', record=record, error=str(e))

    # Generate dynamic due dates
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]
    return render_template('edit_record.html', record=record, due_dates=due_dates)

# Delete record route
@app.route('/delete/<int:id>', methods=['GET'])
def delete_record(id):
    record = TaxPayment.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))

# Filter route for AJAX
@app.route('/filter', methods=['POST'])
def filter_records():
    selected_due_date = request.json.get('due_date')

    # Fetch filtered or all records
    if selected_due_date:
        records = TaxPayment.query.filter_by(due_date=selected_due_date).all()
    else:
        records = TaxPayment.query.all()

    # Calculate summary
    total_amount = sum(record.amount for record in records)
    tax_rate = 0.06  # 6% tax rate
    tax_due = total_amount * tax_rate

    # Prepare response
    records_data = [
        {
            'id': record.id,
            'company': record.company,
            'amount': f"${record.amount:,.2f}",
            'payment_date': record.payment_date or "N/A",
            'status': record.status,
            'due_date': record.due_date,
        } for record in records
    ]

    return jsonify({
        'records': records_data,
        'total_amount': f"${total_amount:,.2f}",
        'tax_rate': f"{tax_rate * 100}%",
        'tax_due': f"${tax_due:,.2f}",
    })

if __name__ == '__main__':
    app.run(debug=True)
