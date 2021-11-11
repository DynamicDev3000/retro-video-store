from app import db
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models.video import Video
from app.models.customer import Customer


videos_bp = Blueprint("videos", __name__, url_prefix=("/videos"))

#POST/CREATE 
@videos_bp.route("",methods=["POST"])
def post_videos():
    request_body = request.get_json()
    if "title" not in request_body:
        return{
            "details": "Request body must include title."
        }, 400
    
    elif "release_date" not in request_body:
        return{
            "details": "Request body must include release_date."
        }, 400
    
    elif "total_inventory" not in request_body:
        return{
            "details": "Request body must include total_inventory."
        }, 400

    new_video = Video(
        title = request_body["title"], 
        release_date = request_body["release_date"],
        total_inventory = request_body["total_inventory"]
    )
    db.session.add(new_video)
    db.session.commit()

    return jsonify(new_video.to_video_object()), 201

#GET
@videos_bp.route("", methods=["GET"])
def get_videos():
    videos = Video.query.all()
    videos_response = []
    for video in videos:
        videos_response.append(video.to_video_object())
    return jsonify(videos_response), 200

@videos_bp.route("/<video_id>",methods=["GET"])
def get_video(video_id):
    if video_id.isnumeric() != True:
        return {"message": "Video id provided is not a number."}, 400
    
    video = Video.query.get(video_id)

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404
        

    return{
        "id": video.id,
        "title": video.title,
        "release_date": datetime.now(),
        "total_inventory": video.total_inventory
    }
#PUT
@videos_bp.route("/<video_id>",methods=["PUT"])
def update_video(video_id):
    video = Video.query.get(video_id)
    request_body = request.get_json()

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404

    if "title" not in request_body or "release_date" not in request_body or "total_inventory" not in request_body:
        return {
            "details": "Invalid data"
        }, 400

    video.title = request_body["title"]
    video.release_date = request_body["release_date"]
    video.total_inventory = request_body["total_inventory"]

    db.session.commit()

    return {
        "id": video.id,
        "title": video.title,
        "release_date": datetime.now(),
        "total_inventory": video.total_inventory
    }
#DELETE
@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_video(video_id):

    video = Video.query.get(video_id)

    if video is None:
        return {"message": f"Video {video_id} was not found"}, 404

    db.session.delete(video)
    db.session.commit()

    return jsonify({"id": video.id}), 200

###Customer

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

@customers_bp.route("", methods=["POST"])
def post_customer():
    request_body = request.get_json()

    if "name" not in request_body:
        return {"details": "Request body must include name."}, 400
    elif "postal_code" not in request_body:
        return {"details": "Request body must include postal_code."}, 400
    elif "phone" not in request_body:
        return {"details": "Request body must include phone."}, 400

    new_customer = Customer(
        name = request_body["name"],
        #registered_at = request_body["registered_at"],
        postal_code = request_body["postal_code"],
        phone = request_body["phone"]
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"id": new_customer.id}), 201

#Get
@customers_bp.route("", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    customers_response = []

    for customer in customers:
        customers_response.append(
            {
            "id" : customer.id,
            "name" : customer.name,
            "postal_code" : customer.postal_code,
            "phone" : customer.phone,
            "registered_at" : datetime.now()
            }
        )
    return jsonify(customers_response), 200

@customers_bp.route("/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    if customer_id.isnumeric() != True:
        return {"message": "Customer id provided is not a number."}, 400
    
    customer = Customer.query.get(customer_id)

    if customer is None:
        return {"message": f"Customer {customer_id} was not found"}, 404

    return {
        "id" : customer.id,
        "name" : customer.name,
        "postal_code" : customer.postal_code,
        "phone" : customer.phone
    }
@customers_bp.route("/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    request_body = request.get_json()
    
    if customer is None:
        return {"message": f"Customer {customer_id} was not found"}, 404

    if "name" not in request_body or "postal_code" not in request_body or "phone" not in request_body:
        return {
        "details": "Invalid data"
        }, 400
        
    customer.name = request_body["name"]
    customer.phone = request_body["phone"]
    customer.postal_code = request_body["postal_code"]
    
    db.session.commit()

    return {
        "id" : customer.id,
        "name" : customer.name,
        "postal_code" : customer.postal_code,
        "phone" : customer.phone,
        "registered_at" : datetime.now()
    }

@customers_bp.route("/<customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    customer = Customer.query.get(customer_id)

    if customer is None:
        return {"message": f"Customer {customer_id} was not found"}, 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"id": customer.id}), 200
