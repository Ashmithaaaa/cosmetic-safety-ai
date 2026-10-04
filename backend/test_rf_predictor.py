from backend.rf_predictor import predict_skin_sensitization


test_smiles = "CCO"

result = predict_skin_sensitization(test_smiles)

print("SMILES:", test_smiles)
print("Prediction result:")
print(result)