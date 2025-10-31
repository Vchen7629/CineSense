import pandas as pd
import os

def preprocess_data() -> None:
    current_dir = os.path.dirname(__file__)
    input_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "ratings.csv")
    output_path = os.path.join(current_dir, "..", "datasets", "output", "ml-latest-small-output.csv")

    df = pd.read_csv(input_path)

    # filter original dataset for positive ratings only (greater than 3.0 rating)
    positive_ratings = df["rating"] > 3.0

    # Create a new df with only the positive ratings users and no timestamp column
    filtered_df = df[positive_ratings].drop(columns=["timestamp"])

    # normalize the ratings to 1
    filtered_df["rating"] = 1

    print(filtered_df)

    # write the processed dataset to a csv
    filtered_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    preprocess_data()