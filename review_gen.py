import random
import datetime
import json

end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

print(start, end)

restaurants = [
    ("Midtown", 4.0),
    ("Buckhead", 3.5),
    ("Old Fourth Ward", 2.0), 
    ("GT Campus", 5.0),
    ("Cabbagetown", 3.5)
]
dishes = [
    ('Squid Fries', 3.0),  
    ('Feta Cheese Pasta', 5.0),  
    ('Ricotta Cheese Salad', 4.2),  
    ('Pyon Baek Steamed', 4.1),  
    ('Tomato Oil Pasta', 3.2),  
    ('Sweet Potato Fries', 1.0),  
    ('Lamb Skewer', 4.6),  
    ('Tteokbokki', 4.4),  
    ('Bacon Wrapped Pineapple', 3.8)
]
def random_dt():
    date = start + random.random() * (end - start)
    date = date.replace(hour=random.randint(9, 21))
    return date

def get_review(mean, std):
    return int(max(1, min(5, random.normalvariate(mean, std))))

def mean(reviews):
    return sum(reviews) / float(len(reviews))

reviews = []
for i in range(1200):
    review = {}
    dt = random_dt()
    dish_name, dish_rating = random.choice(dishes)
    restaurant, restaurant_vibe = random.choice(restaurants)
    review['time'] = str(dt)
    review['dish'] = dish_name
    review['restaurant'] = restaurant
    review['food'] = get_review(dish_rating, 1)
    review['food_taste'] = get_review(4.5 if dt.weekday() in [3,4] else 3.5, 1)
    review['food_portion'] = get_review(3.5, 1)
    review['food_look'] = get_review(3.5, 1)
    review['service'] = get_review(2.5 if (dt.hour >= 12 and dt.hour <= 15) and restaurant == "Buckhead" else 4.5, 1)
    review['vibe'] = get_review(restaurant_vibe, 1.5)
    review['overall'] = get_review(mean([review['food'], review['service'], review['vibe']]), 1)
    reviews.append(review)

with open("reviews.json", "w") as f:
    f.writelines(json.dumps(reviews, indent=2))