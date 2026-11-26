import pandas as pd
import numpy as np


def generate_data_insights(df):

    insights = []

    rows, columns = df.shape

    # Dataset size
    insights.append(
        f"Your dataset contains {rows} rows "
        f"and {columns} columns."
    )

    # Missing values
    missing = df.isnull().sum()
    missing_columns = missing[missing > 0]

    if not missing_columns.empty:
        for column, count in missing_columns.items():
            percentage = (count / rows) * 100

            insights.append(
                f"{column} contains {count} missing values "
                f"({percentage:.2f}%)."
            )
    else:
        insights.append(
            "Great! No missing values were detected."
        )

    # Duplicate rows and repeated values
    duplicates = df.duplicated().sum()

    repeated_value_groups = 0

    for column in df.columns:
        counts = df[column].dropna().value_counts()
        repeated_value_groups += int((counts > 1).sum())

    if duplicates > 0:
        insights.append(
            f"Found {duplicates} completely duplicate rows."
        )
    else:
        insights.append(
            "No completely duplicate rows were found."
        )

    if repeated_value_groups > 0:
        insights.append(
            f"Found {repeated_value_groups} repeated value groups "
            "within individual columns."
        )

    # Numerical analysis
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        if df[column].dropna().empty:
            continue

        mean_value = df[column].mean()
        max_value = df[column].max()
        min_value = df[column].min()

        insights.append(
            f"{column}: Average = {mean_value:.2f}, "
            f"Maximum = {max_value:.2f}, "
            f"Minimum = {min_value:.2f}."
        )

    # Categorical analysis
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns

    for column in categorical_columns:

        counts = df[column].value_counts()

        if not counts.empty:
            top_category = counts.index[0]

            insights.append(
                f"In {column}, the most frequent value "
                f"is {top_category} "
                f"({counts.iloc[0]} occurrences)."
            )

    return insights


def clean_dataset(df, strategy="median"):

    cleaned_df = df.copy()

    # Remove duplicate records
    cleaned_df = cleaned_df.drop_duplicates()

    # Handle missing values
    for column in cleaned_df.columns:

        if cleaned_df[column].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(
            cleaned_df[column]
        ):

            if strategy == "median":
                cleaned_df[column] = (
                    cleaned_df[column].fillna(
                        cleaned_df[column].median()
                    )
                )

            elif strategy == "mean":
                cleaned_df[column] = (
                    cleaned_df[column].fillna(
                        cleaned_df[column].mean()
                    )
                )

        else:

            if strategy == "mode":
                modes = cleaned_df[column].mode()

                if not modes.empty:
                    cleaned_df[column] = (
                        cleaned_df[column].fillna(modes.iloc[0])
                    )

    return cleaned_df
