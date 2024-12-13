from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tax_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define TaxPayment model
class TaxPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # paid/unpaid
    due_date = db.Column(db.String(50), nullable=False)

# Ensure tables are created once
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True

# Home route

@app.route('/', methods=['GET', 'POST'])
def index():
    from datetime import datetime

    # Generate due dates dynamically
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]

    # Check if a filter is applied
    selected_due_date = request.form.get('due_date') if request.method == 'POST' else None

    # Fetch filtered or all records
    if selected_due_date:
        records = TaxPayment.query.filter_by(due_date=selected_due_date).all()
    else:
        records = TaxPayment.query.all()

    return render_template('index.html', records=records, due_dates=due_dates, selected_due_date=selected_due_date)



# Route to add records
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        # Get form data
        company = request.form['company']
        amount = float(request.form['amount'])
        payment_date = request.form['payment_date'] or None
        status = request.form['status']
        due_date = request.form['due_date']

        # Create a new record
        new_record = TaxPayment(company=company, amount=amount, payment_date=payment_date, status=status, due_date=due_date)
        db.session.add(new_record)
        db.session.commit()

        return redirect(url_for('index'))

    # Generate due dates dynamically
    from datetime import datetime
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]

    return render_template('add_record.html', due_dates=due_dates)

@app.route('/delete/<int:id>', methods=['GET'])
def delete_record(id):
    record = TaxPayment.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    record = TaxPayment.query.get_or_404(id)

    if request.method == 'POST':
        # Update the record with form data
        record.company = request.form['company']
        record.amount = float(request.form['amount'])
        record.payment_date = request.form['payment_date'] or None
        record.status = request.form['status']
        record.due_date = request.form['due_date']

        db.session.commit()
        return redirect(url_for('index'))

    # Generate due dates dynamically
    from datetime import datetime
    current_year = datetime.now().year
    due_dates = [
        f"April 15, {current_year}",
        f"June 15, {current_year}",
        f"September 15, {current_year}",
        f"January 15, {current_year + 1}"
    ]

    return render_template('edit_record.html', record=record, due_dates=due_dates)



if __name__ == '__main__':
    app.run(debug=True)
