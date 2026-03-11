from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_ID = 7117775366
GATEWAY_TOKEN = "Z4KDJHDLB9VTGT0Y"
GATEWAY_KEY = "49um9Ok94oPxVbvUhBpCfEiU"

# Yeh data temporary hai (Server restart pe reset ho jayega)
# Permanent ke liye aapko Supabase use karna hoga
app_settings = {"withdraw_enabled": True}
banned_users = set() # Telegram IDs
banned_numbers = set() # Phone Numbers

@app.route('/')
def home():
    return render_template('index.html')

# --- USER API ---
@app.route('/api/withdraw', methods=['POST'])
def process_withdraw():
    data = request.json
    u_id = data.get('user_id')
    num = data.get('number')
    amt = data.get('amount')

    if not app_settings['withdraw_enabled']:
        return jsonify({"status": "error", "message": "Withdrawal is paused by Admin."})
    
    if str(u_id) in banned_users or str(num) in banned_numbers:
        return jsonify({"status": "error", "message": "You or this number is banned!"})

    # Calling Saathi Gateway
    api_url = f"https://saathigateway.com/api?token={GATEWAY_TOKEN}&key={GATEWAY_KEY}&paytoNumber={num}&amount={amt}&comment=CashRoll_Rewards"
    
    try:
        r = requests.get(api_url)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": "API Connection Failed"})

# --- ADMIN API ---
@app.route('/api/admin/action', methods=['POST'])
def admin_action():
    data = request.json
    if int(data.get('admin_id')) != ADMIN_ID:
        return jsonify({"status": "unauthorized"}), 403

    action = data.get('action')
    
    if action == "toggle_withdraw":
        app_settings['withdraw_enabled'] = not app_settings['withdraw_enabled']
        return jsonify({"status": "success", "new_state": app_settings['withdraw_enabled']})
    
    elif action == "ban_user":
        target = str(data.get('target'))
        banned_users.add(target)
        return jsonify({"status": "success", "message": f"User {target} banned"})

    elif action == "ban_number":
        target = str(data.get('target'))
        banned_numbers.add(target)
        return jsonify({"status": "success", "message": f"Number {target} banned"})

    return jsonify({"status": "invalid_action"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
