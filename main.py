# Author: Dhaval Patel. Codebasics YouTube Channel

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import re
import generic_helper
from datetime import datetime, time

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

    # Detect active context names
    context_names = [ctx['name'].split('/')[-1] for ctx in output_contexts]
    is_new_order = 'new-order-context' in context_names

    # Intent handlers
    intent_handler_dict = {
        'User.ThankYou': thank_you_response,
        'Shop.Hours': shop_hours,
        'Order.Start': start_new_order,
        'Order.add - context: ongoing-order': lambda p, s: add_to_order(p, s, is_new_order),
        'Order.Remove - context: ongoing-order': remove_from_order,
        'Order.Complete - context: Ongoing-order': complete_order,
        'tracking.order - context: ongoing-tracking': lambda p, s: track_order(p)
    }

    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters, session_id)

    return JSONResponse(content={
        "fulfillmentText": "Sorry, I didn't understand that."
    })


def thank_you_response(parameters: dict, session_id: str):
    return JSONResponse(content={
        "fulfillmentText": "You're welcome! Let me know if you'd like to place a new order or track one."
    })



def start_new_order(parameters: dict, session_id: str):
    # Clear previous order data
    inprogress_orders[session_id] = {}
    return JSONResponse(content={
        'fulfillmentText': "Okay, I've cleared your previous order. What would you like to order now?"
    })


def shop_hours(parameters: dict, session_id: str):
    # Define shop open and close times
    open_time = time(9, 0)    # 9:00 AM
    close_time = time(22, 0)  # 10:00 PM

    current_time = datetime.now().time()

    # Determine if shop is currently open
    if open_time <= current_time <= close_time:
        status = "Yes, we’re open now."
    else:
        status = "Sorry, we’re currently closed."

    fulfillment_text = (
        f"{status} Our shop is open from 9:00 AM to 10:00 PM daily."
    )

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str, is_new_order: bool = False):
    food_items = parameters.get("food-item", [])

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

        if is_new_order or session_id not in inprogress_orders:
            inprogress_orders[session_id] = new_food_dict
        else:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order please?"
        })

    food_items = parameters["food-item"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item in current_order:
            removed_items.append(item)
            del current_order[item]
        else:
            no_such_items.append(item)

    fulfillment_text = ""

    if removed_items:
        fulfillment_text += f'Removed {", ".join(removed_items)} from your order!'

    if no_such_items:
        fulfillment_text += f' Your current order does not have {", ".join(no_such_items)}.'

    if not current_order:
        fulfillment_text += " Your order is now empty."
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what’s left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders or not inprogress_orders[session_id]:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please place a new order again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We've placed your order. Your order ID is #{order_id}. Your total is {order_total}. You can pay on delivery."

        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        db_helper.insert_order_item(food_item, quantity, next_order_id)

    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


def track_order(parameters: dict):
    order_id_param = parameters.get('order_id')

    if not order_id_param:
        return JSONResponse(content={
            'fulfillmentText': f"I could not find an order ID in your request. Parameters: {parameters}"
        })

    if isinstance(order_id_param, list):
        order_id = order_id_param[0]
    else:
        order_id = order_id_param

    order_id = int(order_id)
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f'The order status for order ID {order_id} is: {order_status}'
    else:
        fulfillment_text = f'No order found with ID {order_id}'

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })
