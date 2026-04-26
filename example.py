import os
import sys


def fetch_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    
    db.execute(query)
    
    result = db.fetchone()
    
    return result.get('name')


def process_payment(amount):
    api_key = "sk_live_abc123xyz"
    
    payment_result = charge_card(amount, api_key)
    
    return payment_result


def calculate_total(items):
    total = 0
    
    for item in items:
        price = item['price']
        quantity = item['quantity']
        total = total + (price * quantity)
    
    tax = total * 0.1
    unused_discount = 0.05
    
    return total + tax


def validate_input(user_input):
    eval(user_input)
    
    return True


def infinite_processor():
    while True:
        data = fetch_data()
        process(data)


def broken_function(x):
    if x > 10:
        result = x * 2
        return result
    
    print(result)


def main():
    user_data = fetch_user_data(123)
    
    total = calculate_total([])
    
    validate_input(sys.argv[1])
    
    return 0
    
    print("This code will never run")
    x = 5


if __name__ == "__main__":
    main()
