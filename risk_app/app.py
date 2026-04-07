from flask import Flask, render_template, request, flash
import logging
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-this")

# Configure logging
logging.basicConfig(level=logging.INFO)


def validate_inputs(age, income, past_claims):
    errors = []

    if age < 18 or age > 100:
        errors.append("Age must be between 18 and 100 years")
    if income < 0:
        errors.append("Income cannot be negative")
    if past_claims < 0:
        errors.append("Past claims cannot be negative")
    if past_claims > 10:
        errors.append("Past claims seems unusually high, please verify")

    return errors


def compute_risk(age, income, smoking, vehicle_type, past_claims):
    # Age factor
    if age < 25:
        risk = 20
        age_factor = "Young driver (+20)"
    elif age < 40:
        risk = 10
        age_factor = "Adult driver (+10)"
    else:
        risk = 5
        age_factor = "Experienced driver (+5)"

    # Smoking factor
    if smoking == "yes":
        risk += 30
        smoking_factor = "Smoker (+30)"
    else:
        smoking_factor = "Non-smoker (0)"

    # Claims factor
    if past_claims == 0:
        claims_factor = "No claims (0)"
    elif past_claims <= 2:
        risk += 15
        claims_factor = f"Few claims ({past_claims}) (+15)"
    else:
        risk += 30
        claims_factor = f"Multiple claims ({past_claims}) (+30)"

    # Income factor
    if income < 300000:
        risk += 10
        income_factor = "Low income (+10)"
    elif income < 800000:
        risk += 5
        income_factor = "Middle income (+5)"
    else:
        income_factor = "High income (0)"

    # Vehicle factor
    if vehicle_type == "sports":
        risk += 25
        vehicle_factor = "Sports car (+25)"
    elif vehicle_type == "suv":
        risk += 10
        vehicle_factor = "SUV (+10)"
    else:
        vehicle_factor = "Standard vehicle (+5)"
        risk += 5

    # Clamp risk between 0-100
    risk = min(100, max(0, risk))

    # Calculate premium
    base_premium = 5000
    premium = base_premium + (risk * 120)

    # Additional premium adjustments
    if smoking == "yes" and vehicle_type == "sports":
        premium += 2000
    if past_claims > 2 and age < 25:
        premium += 1500

    # Determine category and label
    if risk < 30:
        category = "Low"
        label = "🟢 Low Risk"
        recommendation = "Your risk profile is excellent! You qualify for standard coverage with potential discounts."
    elif risk < 60:
        category = "Medium"
        label = "🟠 Medium Risk"
        recommendation = "Moderate risk profile. Consider lifestyle changes to improve your risk score."
    else:
        category = "High"
        label = "🔴 High Risk"
        recommendation = "High risk detected. Specialized coverage required. Consider risk reduction measures."

    breakdown = {
        'age_factor': age_factor,
        'smoking_factor': smoking_factor,
        'claims_factor': claims_factor,
        'income_factor': income_factor,
        'vehicle_factor': vehicle_factor
    }

    return risk, premium, category, label, recommendation, breakdown


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Get form data with safe defaults
            age = int(request.form.get("age") or 0)
            income = int(request.form.get("income") or 0)
            past_claims = int(request.form.get("claims") or 0)
            smoking = request.form.get("smoking", "no")
            vehicle_type = request.form.get("vehicle", "normal")

            # Validate inputs
            errors = validate_inputs(age, income, past_claims)

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template(
                    "index.html",
                    age=age,
                    income=income,
                    smoking=smoking,
                    vehicle=vehicle_type,
                    claims=past_claims
                )

            # Calculate risk and premium
            risk, premium, category, label, recommendation, breakdown = compute_risk(
                age, income, smoking, vehicle_type, past_claims
            )

            # Render result.html (make sure this file exists in templates folder)
            return render_template(
                "result.html",
                risk=risk,
                premium=premium,
                category=category,
                label=label,
                recommendation=recommendation,
                breakdown=breakdown
            )

        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "error")
            return render_template("index.html")

    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)