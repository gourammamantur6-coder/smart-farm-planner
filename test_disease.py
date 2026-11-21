from ai_weather.disease_detection import detect_disease

print("Starting disease detection...")

result = detect_disease("test_leaf.jpg")

print("\nPlant Disease Detection Result:")
print(result)