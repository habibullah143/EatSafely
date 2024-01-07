from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pymongo
import pandas as pd
import json

mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
db = mongo_client['MyFYP']
collection = db['food_products']

# Initialize the Multinomial Naive Bayes classifier
vectorizer = CountVectorizer()
clf = MultinomialNB()

def load_model():
    global vectorizer, clf

    # Fetch data from MongoDB for training
    cursor = collection.find()
    df = pd.DataFrame(list(cursor))

    # Prepare data for cuisine prediction
    X = df['Ingredients']
    y = df['Cuisine Uses']

    # Convert Ingredients to numerical using CountVectorizer
    X = vectorizer.fit_transform(X)

    # Train the model
    clf.fit(X, y)

# Load the model on application startup
load_model()

def haram_halal_detection(request, barcode):
    product = collection.find_one({'Barcode number': int(barcode)})
    if not product:
        return JsonResponse({"error": "Product not found in the database."})
    haram_halal_status = "Halal" if product['Haram/Halal'] == 1 else "Haram"
    return JsonResponse({"result": haram_halal_status})

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['Food product name', 'Brand', 'Country of origin', 'Barcode number', 'Haram/Halal', 'Allergen information', 'Ingredients', 'Cuisine Uses']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            # Insert new product into MongoDB
            collection.insert_one(data)

            # Update the Naive Bayes model
            load_model()

            return JsonResponse({"result": "Product added successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def allergic_detection(request, barcode):
    product = collection.find_one({'Barcode number': int(barcode)})
    if not product:
        return JsonResponse({"error": "Product not found in the database."})

    allergic_ingredient = request.GET.get('allergic_ingredient', '').upper()
    
    if not allergic_ingredient:
        return JsonResponse({"error": "Please provide an allergic ingredient parameter."})

    if allergic_ingredient in product['Ingredients'].upper():
        return JsonResponse({"result": f"Warning: The product contains {allergic_ingredient} and may not be safe for you."})
    else:
        return JsonResponse({"result": f"The product is safe for you."})

def cuisine_uses_prediction(request, barcode):
    product = collection.find_one({'Barcode number': int(barcode)})
    if not product:
        return JsonResponse({"error": "Product not found in the database."})
    ingredient_to_predict = product['Ingredients']
    ingredient_to_predict_transformed = vectorizer.transform([ingredient_to_predict])
    cuisine_prediction = clf.predict(ingredient_to_predict_transformed)[0]
    return JsonResponse({"result": cuisine_prediction})
