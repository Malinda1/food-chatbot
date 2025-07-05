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
        #'order.remove - context: ongoing-order': remove_from_order,
        #'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }
       
    return intent_handler_dict[intent](parameters, session_id)

       

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