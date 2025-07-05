# Telegram Food Order Chatbot

A conversational food ordering chatbot for Telegram, powered by AI and Dialogflow, with a FastAPI backend, Grok API, and MySQL database. Users can place, modify, and track food orders using natural language.

---

## Features

- **Telegram Integration:** Users interact with the bot directly in Telegram.
- **Dialogflow AI:** Handles user intent recognition and parameter extraction.
- **FastAPI Backend:** Receives webhook calls from Dialogflow and processes intents.
- **MySQL Database:** Stores menu, orders, and order tracking.
- **Order Management:** Start, add, remove, and complete orders.
- **Order Tracking:** Users can check the status of their orders.
- **Shop Info:** Users can ask for shop hours.
- **Thank You Handling:** Friendly responses to user gratitude.

---

## Supported Intents

The following Dialogflow intents are mapped in `main.py`:

| Intent Name                                 | Handler Function         | Description                                              |
|---------------------------------------------|-------------------------|----------------------------------------------------------|
| `User.ThankYou`                             | `thank_you_response`    | Responds to user gratitude.                              |
| `Shop.Hours`                                | `shop_hours`            | Provides shop opening hours.                             |
| `Order.Start`                               | `start_new_order`       | Starts a new order session, clearing previous data.      |
| `Order.add - context: ongoing-order`        | `add_to_order`          | Adds items to the current order.                         |
| `Order.Remove - context: ongoing-order`     | `remove_from_order`     | Removes items from the current order.                    |
| `Order.Complete - context: Ongoing-order`   | `complete_order`        | Completes and saves the order to the database.           |
| `tracking.order - context: ongoing-tracking`| `track_order`           | Tracks the status of an order by order ID.               |

---

## Project Structure

- `main.py` — FastAPI app, intent routing, and order logic.
- `db_helper.py` — Database connection and queries.
- `generic_helper.py` — Utility functions for session and order parsing.
- `frontend/` — Static files for web frontend (optional).
- `db/pandeyji_eatery.sql` — MySQL schema and sample data.
- `requirements.txt` — Python dependencies.
- `setup_venv.py` — Script to set up virtual environment and `.env` file.

---

## How It Works

1. **User interacts with the Telegram bot.**
2. **Telegram forwards messages to Dialogflow.**
3. **Dialogflow detects intent and sends a webhook request to FastAPI (`main.py`).**
4. **FastAPI processes the intent using the mapped handler function.**
5. **Order data is managed in-memory and persisted to MySQL on completion.**
6. **Responses are sent back to the user via Dialogflow and Telegram.**

---

## Setup Instructions

1. **Clone the repository**

2. **Set up the database**
   - Import `db/pandeyji_eatery.sql` into your MySQL server.

3. **Configure environment**
   - Run:
     ```sh
     python3 setup_venv.py
     ```
   - Update `.env` with your DB credentials and API keys.

4. **Activate the virtual environment**
   - On Mac/Linux:
     ```sh
     source venv/bin/activate
     ```
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```

5. **Run the FastAPI server**
   ```sh
   uvicorn main:app --reload
   ```

6. **Dialogflow & Telegram Setup**
   - Set up Dialogflow agent with the listed intents.
   - Point Dialogflow webhook to your FastAPI endpoint.
   - Connect Telegram bot to Dialogflow using the Telegram API.

---

## Customization

- Update menu items in the database as needed.
- Modify intent handlers in `main.py` for custom logic.
- Adjust frontend in `frontend/` if you want a web interface.

---

## License

MIT License

---

**Author:** Dhaval Patel