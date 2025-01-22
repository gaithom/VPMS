from flask import Flask, render_template_string, request, redirect, flash, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Parking Slot Class
class ParkingSlot:
    def __init__(self, slot_number):
        self.slot_number = slot_number
        self.is_occupied = False
        self.vehicle = None
        self.entry_time = None

# Vehicle Class
class Vehicle:
    def __init__(self, reg_number, vehicle_type):
        self.reg_number = reg_number
        self.vehicle_type = vehicle_type

# Simulate Parking Slots
total_slots = 10
slots = [ParkingSlot(i + 1) for i in range(total_slots)]

# Hardcoded user credentials (for demo purposes)
USER_CREDENTIALS = {
    "admin": "password123"
}

# Flask Routes

@app.route('/')
def index():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    available_slots = len([slot for slot in slots if not slot.is_occupied])
    return render_template_string(TEMPLATE, slots=slots, available_slots=available_slots, total_slots=total_slots)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to index page
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if credentials match
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['username'] = username  # Store username in session
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/available')
def available_slots():
    # Show only available slots
    available_slots = [slot for slot in slots if not slot.is_occupied]
    return render_template_string(AVAILABLE_SLOTS_TEMPLATE, available_slots=available_slots)

@app.route('/park', methods=['POST'])
def park_vehicle():
    reg_number = request.form.get('reg_number').strip()
    vehicle_type = request.form.get('vehicle_type').strip()


    if not reg_number or not vehicle_type:
        flash("Please fill out both fields!", "danger")
        return redirect(url_for('index'))

    # Find an available slot
    available_slot = next((slot for slot in slots if not slot.is_occupied), None)
    if available_slot is None:
        flash("No available slots!", "warning")
        return redirect(url_for('index'))

    # Park the vehicle
    vehicle = Vehicle(reg_number, vehicle_type)
    available_slot.is_occupied = True
    available_slot.vehicle = vehicle
    available_slot.entry_time = datetime.now()

    flash(f"Vehicle {reg_number} parked at Slot {available_slot.slot_number}.", "success")
    return redirect(url_for('index'))

@app.route('/remove', methods=['POST'])
def remove_vehicle():
    reg_number = request.form.get('remove_reg_number').strip()

    if not reg_number:
        flash("Please enter the registration number!", "danger")
        return redirect(url_for('index'))

    # Remove vehicle
    for slot in slots:
        if slot.is_occupied and slot.vehicle.reg_number == reg_number:
            duration = datetime.now() - slot.entry_time
            hours = max(1, duration.total_seconds() // 3600)  # At least 1 hour
            fee = 10 * hours  # ksh 10/hour
            slot.is_occupied = False
            slot.vehicle = None
            slot.entry_time = None

            flash(f"Vehicle {reg_number} removed. Total Fee: ksh {fee:.2f}", "success")
            return redirect(url_for('index'))

    flash(f"Vehicle {reg_number} not found in the parking lot.", "warning")
    return redirect(url_for('index'))

# HTML Templates

# Main Template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parking Management System</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h2 class="text-center mb-4">Vehicle Parking Management System</h2>

        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Display Parking Slots -->
        <h4>Total Slots: {{ total_slots }} | Available Slots: {{ available_slots }} | Occupied: {{ total_slots - available_slots }}</h4>

        <table class="table mt-4">
            <thead>
                <tr>
                    <th>Slot Number</th>
                    <th>Vehicle Registration</th>
                    <th>Vehicle Type</th>
                    <th>Entry Time</th>
                </tr>
            </thead>
            <tbody>
                {% for slot in slots %}
                    <tr>
                        <td>{{ slot.slot_number }}</td>
                        <td>{{ slot.vehicle.reg_number if slot.is_occupied else 'N/A' }}</td>
                        <td>{{ slot.vehicle.vehicle_type if slot.is_occupied else 'N/A' }}</td>
                        <td>{{ slot.entry_time if slot.is_occupied else 'N/A' }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- Show Available Slots Button -->
        <a href="{{ url_for('available_slots') }}" class="btn btn-info mt-4">Show Available Slots</a>

        <!-- Park Vehicle Form -->
        <h4 class="mt-4">Park Vehicle</h4>
        <form method="post" action="{{ url_for('park_vehicle') }}">
            <div class="mb-3">
                <label for="reg_number" class="form-label">Vehicle Registration Number</label>
                <input type="text" class="form-control" id="reg_number" name="reg_number" required>
            </div>
            <div class="mb-3">
                <label for="vehicle_type" class="form-label">Vehicle Type</label>
                <input type="text" class="form-control" id="vehicle_type" name="vehicle_type" required>
            </div>
            <button type="submit" class="btn btn-primary">Park Vehicle</button>
        </form>

        <!-- Remove Vehicle Form -->
        <h4 class="mt-4">Remove Vehicle</h4>
        <form method="post" action="{{ url_for('remove_vehicle') }}">
            <div class="mb-3">
                <label for="remove_reg_number" class="form-label">Vehicle Registration Number</label>
                <input type="text" class="form-control" id="remove_reg_number" name="remove_reg_number" required>
            </div>
            <button type="submit" class="btn btn-danger">Remove Vehicle</button>
        </form>

        <!-- Logout Button -->
        <a href="{{ url_for('logout') }}" class="btn btn-warning mt-4">Logout</a>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Login Template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h2 class="text-center mb-4">Login</h2>

        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="post">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Available Slots Template
AVAILABLE_SLOTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Available Slots</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h2 class="text-center mb-4">Available Parking Slots</h2>

        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Available Slots Table -->
        <table class="table">
            <thead>
                <tr>
                    <th>Slot Number</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for slot in available_slots %}
                    <tr>
                        <td>{{ slot.slot_number }}</td>
                        <td>Available</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>

        <a href="{{ url_for('index') }}" class="btn btn-info">Back to Dashboard</a>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)