import joblib
import pandas as pd
from scipy.sparse import hstack

from utils.extract_metadata_features import extract_metadata_features

# Loading model and pipeline encoders
model = joblib.load("../outputs/best_model_final.pkl")
bert_model = joblib.load("../outputs/bert_model_4cat_meta.pkl")
class_encoder = joblib.load("../outputs/class_encoder_4cat_meta.pkl")
label_encoder = joblib.load("../outputs/label_encoder_4cat_meta.pkl")


def do_prediction(raw_data):
    # 1. Extract metadata features
    raw_data = extract_metadata_features(raw_data)
    # 2. Transform Text (BERT)
    # BERT expects a list/series of strings
    text_embeddings = bert_model.encode(raw_data["comment_sentence"].tolist())
    # 3. Transform Metadata (Category)
    # Class encoder expects a 2D array/DataFrame
    encoded_meta = class_encoder.transform(pd.DataFrame(raw_data["class"].tolist()))
    # 4. Extract Manual columns
    manual_cols = ['comment_length', 'has_params', 'has_code_symbols', 'starts_with_verb', 'has_default']
    manual_features = raw_data[manual_cols].values

    # 5. Concatenate: [Text] + [Categorical Meta] + [Manual Heuristics]
    X_final = hstack([text_embeddings, encoded_meta, manual_features])

    # 6. Predict the target (category)
    prediction_id = model.predict(X_final)

    # 7. Decode to get the string (e.g., "DevelopmentNotes")
    predicted_category = label_encoder.inverse_transform(prediction_id)

    print(f"The Predicted Category is: {predicted_category[0]}")

if __name__ == "__main__":
    raw_data = pd.DataFrame({
        "comment_sentence": ["Request to API fails miserably. Need to change the input variable to String"],
        "class": ["tfprof_logger"]
    })
    do_prediction(raw_data)