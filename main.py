import os
import datetime
import jwt
import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient


app = Flask(__name__, static_folder="static", template_folder="templates")
SECRET_KEY = "supersecretjwtkey"

# Configuring Database
mongodb_connection_string = "mongodb+srv://Admin_Control:Admin_Control@datacluster.nuq2d.mongodb.net/"
mongodb_client = MongoClient(mongodb_connection_string)
database = mongodb_client["Users"]
creds_collection = database["Creds"]
Users_PR_collection = database["Users_PR"]
ScoreCard_collection = database["ScoreCard"]

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    try :

        data = request.json
        username = data.get("username").lower()
        email = data.get("email")
        password = data.get("password")

        print(username, email, password)

        if creds_collection.find_one({"username": username}):
            return jsonify({"success": False, "message": "UserName already exists, Please choose another"})

        if creds_collection.find_one({"email": email}):
            return jsonify({"success": False, "message": "Email already exists"})

        # Get the current count of users and generate a new ID
        user_count = creds_collection.count_documents({})
        new_user_id = user_count + 1
        # Insert the new user into the collection
        creds_collection.insert_one({
            "user_id": new_user_id,
            "username" : username,
            "email": email,
            "password": password
        })


        new_PR_entry = {
                "user_id": new_user_id,
                "username": username}

        New_Score_Entry = { 
            "username" : username,
            "Score" : 0}
        
        Users_PR_collection.insert_one(new_PR_entry)
        ScoreCard_collection.insert_one(New_Score_Entry)


        jwt_payload = {
            ##"user_id": new_user_id,
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
            
        # Generate JWT Token
        token = jwt.encode(
            jwt_payload,
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"success": True,  
                        "token": token, 
                        "username": username.capitalize(), 
                        "message": "Account created successfully"}), 201
    
    except Exception as error:
        print(error)

        return jsonify({"success": False,  
                        "message": "Account creation failed. Please try again later."}), 400




@app.route('/validate_login', methods=['POST'])
def validate_login():

    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and PIN are required"})

    # Fetch user based on email
    user = creds_collection.find_one({"email": email})

    if user and user.get("password") == password:
        print("Password validated")

        jwt_payload = {
        ##"user_id": user["user_id"],
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        
        # Generate JWT Token
        token = jwt.encode(
            jwt_payload,
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"success": True, 
                        "token": token, 
                        "username": user["username"].capitalize(), 
                        "message": "Login Succesfull"})

    return jsonify({"success": False, "message": "Account not Found or Invalid credentials"})


@app.route("/insert_PR", methods=["POST"])
def insert_pr():
    try:
        data = request.json
        
        exercise_name = data.get("exercise_name")
        category, weights, sets, reps = data.get("category"), data.get("weights") ,data.get("sets"), data.get("reps")

        auth_header = request.headers.get("Authorization")
        #print(f"auth_header :", auth_header)
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token missing or invalid"}), 401

        token = auth_header.split(" ")[1]  # Extract the token
        decoded_data = decode_jwt(token)

        username = None

        if(decoded_data["success"]):
            username = decoded_data["user"].get("username")


        if not username or not exercise_name or sets is None or reps is None:
            return jsonify({"success": False, "message": "Missing required fields"})


        user_record = Users_PR_collection.find_one(
                                    {"username": username},
                                    {"_id": 0, "exercises": {"$elemMatch": {"exercise_name": exercise_name}}}
                                )

        result = update_score(username, exercise_name, [weights, sets, reps], user_record)
        if(result["success"]):
            total_score = result["total_score"]
        
        if user_record:

            Users_PR_collection.update_one(
                {"username": username, "exercises.exercise_name": exercise_name},
                {"$set": {
                    "exercises.$.weights": weights, 
                    "exercises.$.sets": sets, 
                    "exercises.$.reps": reps }}
            )

        else:
            # If exercise does not exist, add a new one
            Users_PR_collection.update_one(
                {"username": username},
                {"$push": {"exercises": 
                    {   
                        "category": category,
                        "exercise_name": exercise_name, 
                        "weights": weights, 
                        "sets": sets, 
                        "reps": reps }}}
            )

        
        return jsonify({"success": True, "message": "PR updated","Score": total_score}), 200
    
    except Exception as errors:
        print(errors)

        return jsonify({"success": False, "message": "Something went wrong"}), 400


@app.route("/get_exercises", methods=["GET"])
def get_exercises():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]  # Extract the token
    decoded_data = decode_jwt(token)
    
    username = decoded_data['user'].get("username")

    if username:

        user_data = Users_PR_collection.find_one({"username": username}, {"_id": 0, "exercises": 1})  # Fetch exercises only

        if user_data:
            return jsonify({"success": True, "exercises": user_data["exercises"]})

        else:
            return jsonify({"success": False, "exercises": user_data["exercises"], "message": "Unable to retrive data"})
    else:
        return jsonify({"success": False, "message": "User not found, please Login back"}), 

@app.route("/decode_Token", methods=["POST"])
def decode_token_api():
    result = decode_jwt()  # Call function without argument (token will be extracted from request)
    return jsonify(result)


@app.route("/Fetch_Score", methods=["GET"])
def Fetch_Score_Call():
    username = request.args.get("username")  # Get username from query params
    result = Fetch_Score(username)
    return jsonify(result)  # Ensure response is properly formatted JSON

def Fetch_Score(username=None):
    if username is None:
        results = list(ScoreCard_collection.find({}, {"username": 1, "Score": 1, "_id": 0}))

        if results:
            return {"success": True, "leaderboard": results}
        else:
            return {"success": False, "message": "Unable to fetch leaderboard"}

    else:
        user_data = ScoreCard_collection.find_one({"username": username.lower()}, {"Score": 1, "_id": 0})

        if user_data and "Score" in user_data:
            return {"success": True, "Score": int(user_data["Score"])}
        else:
            return {"success": False, "message": "Unable to retrieve data"}


def decode_jwt(token=None):
    """Decodes a JWT token, whether from a request or passed as an argument."""
    
    # If token is not provided explicitly, extract from request headers
    if token is None:
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "message": "Token missing or invalid"}

        token = auth_header.split(" ")[1]  # Extract token after "Bearer "

    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"success": True, "user": decoded_payload}
    
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Token has expired"}
    
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Invalid token"}

def update_score(username, exercise_name, Current_PR, user_record):
    try:
    
        Inc_score = 0

        if(user_record):

            ## Need to tirm this user_record = {'exercises': [{'exercise_name': 'bicep curl', 'weights': 10, 'sets': 3, 'reps': 10}]}
            user_record = user_record['exercises'][0]
            Pre_weights, Pre_sets, Pre_reps = user_record.get("weights"), user_record.get("sets"), user_record.get("reps")
            
            if(Pre_weights and Pre_sets and Pre_reps):
                if(Current_PR[0] >= Pre_weights):
                    Inc_score += abs(Current_PR[0] - Pre_weights) * 2
                
                if(Current_PR[1] >= Pre_sets):
                    Inc_score += abs(Current_PR[1] - Pre_sets) * 3
                
                if(Current_PR[2] >= Pre_reps):
                    Inc_score += abs(Current_PR[2] - Pre_reps) * 0.5
            
            else:
                print("please check the logs")

            
        else:
            Inc_score = Current_PR[0] * 2 + Current_PR[1] * 3 + Current_PR[2] * 0.5

        
        ScoreCard_collection.update_one(
            {"username": username},
            {"$inc": {"Score": Inc_score}}
        )

        total_score = ScoreCard_collection.find_one({"username": username})["Score"]
        print("score updated", Inc_score, total_score)

        return {"success": True, "message": "Score updated", "total_score": total_score}
    
    
    except Exception as error:
        print(f"error as ",error)




def main():
    app.run(port=int(os.environ.get('PORT', 5000)), debug=True)

if __name__ == "__main__":
    Fetch_Score()
    main()
    
