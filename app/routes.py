from app import db
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.models.video import Video
from app.models.customer import Customer
from app.models.rental import Rental


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
##Rental code
rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")

@rentals_bp.route("/check-out", methods = ["POST"])
def rental_check_out():
    rental_request = request.get_json()

    if "customer_id" not in rental_request or "video_id" not in rental_request:
        return jsonify(details="Request body must include customer id and video id"), 400

    customer_id = rental_request["customer_id"]
    video_id = rental_request["video_id"]

    try: 
        video_id = int(video_id)
        customer_id = int(customer_id)
    except:
        return jsonify(None), 400

    customer = Customer.query.get(customer_id)
    video = Video.query.get(video_id)
    if customer is None or video is None:
        return jsonify(None), 404

    num_currently_checked_out = Rental.query.filter_by(video_id=video.id, checked_out=True).count()
    available_inventory = video.total_inventory - num_currently_checked_out

    if available_inventory == 0:
        return jsonify(message="Could not perform checkout"), 400

    new_rental_check_out= Rental(
        customer_id=customer.id,
        video_id=video.id,
        due_date=(datetime.now() + timedelta(days=7)),
        checked_out=True
    )

    db.session.add(new_rental_check_out)
    db.session.commit()

    available_inventory -= 1

    videos_customer_checked_out = Rental.query.filter_by(customer_id=customer.id, checked_out=True).count()
    return {
        "customer_id": customer.id,
        "video_id": video.id,
        "due_date": new_rental_check_out.due_date,
        "videos_checked_out_count": videos_customer_checked_out,
        "available_inventory": available_inventory
    }, 200


@rentals_bp.route("/check-in", methods = ["POST"])
def rental_check_in():
    rental_request = request.get_json()

    if "customer_id" not in rental_request or "video_id" not in rental_request:
        return jsonify(details="Request body must include customer id and video id"), 400

    customer_id = rental_request["customer_id"]
    video_id = rental_request["video_id"]

    try: 
        video_id = int(video_id)
        customer_id = int(customer_id)
    except:
        return jsonify(None), 400

    customer = Customer.query.get(customer_id)
    video = Video.query.get(video_id)

    if customer is None or video is None:
        return jsonify(None), 404
    
    rental = Rental.query.filter_by(customer_id=customer.id, video_id=video.id, checked_out=True).first()
    if rental is None:
        return jsonify(message=f"No outstanding rentals for customer {customer.id} and video {video.id}"), 400

    rental.checked_out = False
    db.session.commit()

    num_currently_checked_out = Rental.query.filter_by(video_id=video.id, checked_out=True).count()
    available_inventory = video.total_inventory - num_currently_checked_out
    videos_customer_checked_out = Rental.query.filter_by(customer_id=customer.id, checked_out=True).count()
    
    return {
        "customer_id": customer.id,
        "video_id": video.id,
        "videos_checked_out_count": videos_customer_checked_out,
        "available_inventory": available_inventory
    }, 200

@customers_bp.route("/<customer_id>/rentals", methods=["GET"]) 
def get_customers_current_rentals(customer_id):
    """
    List of videos a customer currently has checked out
    """
    try: 
        customer_id = int(customer_id)
    except:
        return jsonify(None), 400
    
    customer = Customer.query.get(customer_id)
    
    if customer == None:
        return jsonify(message=f"Customer {customer_id} was not found"), 404

    rental_list = Rental.query.filter_by(customer_id=customer.id, checked_out=True)

    list_of_dicts = []

    for rental in rental_list:
        
        video = Video.query.get(rental.video_id)
        list_of_dicts.append({
            "release_date": video.release_date,
            "title": video.title,
            "due_date": rental.due_date
        })

    return jsonify(list_of_dicts), 200
    
@videos_bp.route("/<video_id>/rentals", methods=["GET"]) 
def get_customers_with_video_rented(video_id):
    """
    List of all customers with video rented.
    """
    try: 
        video_id = int(video_id)
    except:
        return jsonify(None), 400
    
    video  = Video.query.get(video_id)
    
    if video == None:
        return jsonify(message=f"Video {video_id} was not found"), 404

    rental_list = Rental.query.filter_by(video_id=video.id, checked_out=True)

    list_of_dicts = []

    for rental in rental_list:
        
        customer = Customer.query.get(rental.video_id)
        list_of_dicts.append({
        "due_date": rental.due_date,
        "name": customer.name,
        "phone": customer.phone,
        "postal_code": customer.postal_code
    })

    return jsonify(list_of_dicts), 200