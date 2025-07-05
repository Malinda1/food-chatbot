# Author: Dhaval Patel. Codebasics YouTube Channel

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import re
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()

    # Print the whole payload to debug
    print("Payload:", payload)

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult'].get('outputContexts', [])
    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    if intent == 'tracking.order - context: ongoing-tracking':
        response = track_order(parameters)
        return response

       
    intent_handler_dict = {
        'Order.add - context: ongoing-order': add_to_order,
        'Order.Remove - context: ongoing-order': remove_from_order,
        'Order.Complete - context: Ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }
       
    return intent_handler_dict[intent](parameters, session_id)

       
def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    food_items = parameters["food-item"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })       
       


def add_to_order(parameters: dict, session_id: str):
    

    food_items = parameters.get("food-item", [])

    # Match and sort number keys in reverse to reflect spoken order
    quantity_keys = sorted(
        [key for key in parameters.keys() if re.match(r'^number\d*$', key)],
        key=lambda k: int(re.search(r'\d*$', k).group() or 0),
        reverse=True
    )

    quantities = []
    for key in quantity_keys:
        quantities.extend(parameters.get(key, []))

    if len(food_items) != len(quantities):
        fulfillment_text = f"Sorry, I couldn't match quantities to items. Items: {food_items}, Quantities: {quantities}"
    else:
        
        new_food_dict = dict(zip(food_items, quantities))
        
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict
        
        
    
        
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })



def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)

            fulfillment_text = f"Awesome. We have placed your order. " \
                           f"Here is your order id # {order_id}. " \
                           f"Your order total is {order_total} which you can pay at the time of delivery!"
        
        del inprogress_orders[session_id]
    
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
    
def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )
        
    # Now insert order tracking status
    db_helper.insert_order_tracking(next_order_id, "in progress")
    
    return next_order_id

def track_order(parameters: dict):
    order_id_param = parameters.get('order_id')

    if not order_id_param:
        return JSONResponse(content={
            'fulfillmentText': f"I could not find an order ID in your request. Parameters: {parameters}"
        })

    # Fix: If order_id is a list, extract the first item
    if isinstance(order_id_param, list):
        order_id = order_id_param[0]
    else:
        order_id = order_id_param

    # Optional: cast to int if it's a float
    order_id = int(order_id)

    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f'The order status for order ID {order_id} is: {order_status}'
    else:
        fulfillment_text = f'No order found with ID {order_id}'

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })