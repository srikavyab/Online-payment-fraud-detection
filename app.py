from flask import Flask, render_template, request
import pickle
import pandas as pd
import random
import requests
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# Load the trained model
model = pickle.load(open('../training/onlinepayment.pkl', 'rb'))  # Update the path to your model

# Fast2SMS API key (replace with your actual API key)
FAST2SMS_API_KEY = 'mK58MPa6pL1kWy9FunSchTEXBZsb4CGqQlIdUNHRrtgJOA3ewzkchM3aziEBNAYjvCR1UqTdloGZxn26'  # Replace with your actual API key

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/submit-form', methods=['POST'])
def predict1():
    try:
        # Get input values from the form
        transaction_type = int(request.form.get('type')) 
        amount = float(request.form.get('amount'))
        old_balance_org = float(request.form.get('oldBalanceOrg'))
        new_balance_org = float(request.form.get('newBalanceOrg'))
        user_phone_number = request.form.get('phone')  # Get phone number from form

        # Create a DataFrame with the relevant features
        input_df = pd.DataFrame({
            'type': [transaction_type],
            'amount': [amount],
            'oldbalanceOrg': [old_balance_org],
            'newbalanceOrig': [new_balance_org]
        })

        # Make prediction using the model
        prediction = model.predict(input_df)
        
        if prediction[0] == 1:  # Fraudulent transaction detected
            result_str = "Fraudulent"
            result_class = "fraudulent"
            image_url = "https://www.mywestnipissingnow.com/wp-content/uploads/2019/03/Fraud-1-1.jpg"
            message = "Alert: Your transaction has been flagged as FRAUDULENT. Please review it immediately."

            # Generate OTP
            otp = random.randint(100000, 999999)  # Generate a random OTP
            
            # Send OTP via Fast2SMS
            send_otp(user_phone_number, otp)  # Send OTP using Fast2SMS
            
            message += f" Your OTP is: {otp}"  # Include OTP in message
            
        else:  # Non-fraudulent transaction
            result_str = "Non-Fraudulent"
            result_class = "non-fraudulent"
            image_url = "https://jooinn.com/images/genuine-dice-mean-authentic-legitimate-and-real.jpg"
            message = "Your transaction is confirmed as NON-FRAUDULENT. Thank you for your trust."

        # Render the result page with the image and message
        return render_template('submit.html', result=result_str, result_class=result_class, image_url=image_url)
    except Exception as e:
        return render_template('submit.html', result="Error: " + str(e), result_class="error", image_url=None)  # Error handling

def send_otp(phone_number, otp):
    """Send OTP via SMS using Fast2SMS."""
    try:
        print(f"Sending OTP {otp} to {phone_number}")
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        headers = {
            'authorization': FAST2SMS_API_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'sender_id': 'FSTSMS',
            'message': f'Your OTP is: {otp}',
            'language': 'english',
            'route': 'otp',
            'numbers': phone_number,
        }
        
        response = requests.post(url, headers=headers, data=data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        

        if response.status_code == 200:
            print(f"OTP sent successfully to {phone_number}")
        else:
            print(f"Failed to send OTP: {response.text}")
    
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
