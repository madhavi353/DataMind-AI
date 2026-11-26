import re
import pandas as pd

def find_column(df, question, numeric_only=False):
    """
    Find a dataset column mentioned in the question.
    """

    q = question.lower()

    columns = sorted(
        df.columns,
        key=lambda x: len(str(x)),
        reverse=True
    )

    for column in columns:

        name = str(column).lower()

        if numeric_only and not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            continue

        pattern = r"(?<!\w)" + re.escape(name) + r"(?!\w)"

        if re.search(pattern, q):
            return column

    return None

def get_numeric_column(df, question):

    # Prefer any numeric column explicitly mentioned in the question.
    column = find_column(df, question, numeric_only=True)
    if column:
        return column

    numeric = df.select_dtypes(include="number").columns.tolist()
    return numeric[0] if numeric else None

def get_category_column(df, question):

    column = find_column(df, question)

    if column and not pd.api.types.is_numeric_dtype(df[column]):
        return column

    categorical = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    return categorical[0] if categorical else None

def get_label_column(df, question):
    """Find a place/category column for ranking questions."""

    column = find_column(df, question)

    if column and not pd.api.types.is_numeric_dtype(df[column]):
        return column

    q = question.lower()

    location_aliases = [
        "place", "location", "state", "province", "country",
        "city", "district", "region", "area", "zone"
    ]

    location_requested = any(alias in q for alias in location_aliases)

    categorical = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    categorical = [
        column for column in categorical
        if "id" not in str(column).lower()
    ]

    if location_requested:
        preferred_names = [
            "place", "location", "state", "province", "country",
            "city", "district", "region", "area", "zone"
        ]

        for alias in preferred_names:
            for column in categorical:
                if alias in str(column).lower():
                    return column

    label_aliases = [
        "name", "institute", "school", "college", "university",
        "center", "station", "department", "category", "team", "company"
    ]

    for alias in label_aliases:
        if alias in q:
            for column in categorical:
                if alias in str(column).lower():
                    return column

    return categorical[0] if categorical else None

def get_duplicate_values(df):
    """Return repeated values found within individual columns."""

    duplicate_rows = []

    for column in df.columns:
        series = df[column].dropna()

        if series.empty:
            continue

        counts = series.value_counts(dropna=False)

        for value, count in counts[counts > 1].items():
            duplicate_rows.append({
                "Column": str(column),
                "Repeated Value": str(value),
                "Occurrences": int(count)
            })

    if not duplicate_rows:
        return pd.DataFrame(
            columns=["Column", "Repeated Value", "Occurrences"]
        )

    return pd.DataFrame(duplicate_rows)

def analyze_question(df, question):

    q = question.lower().strip()

    if not q:
        return {
            "answer": "Please enter a question.",
            "data": None,
            "chart": False
        }

    # ----------------------------
    # BASIC DATASET QUESTIONS
    # ----------------------------

    if any(word in q for word in [
        "how many rows", "number of rows",
        "total rows", "row count"
    ]):

        return {
            "answer": f"Your dataset contains {len(df):,} rows.",
            "data": None,
            "chart": False
        }

    if any(word in q for word in [
        "how many columns", "number of columns",
        "total columns", "column count"
    ]):

        return {
            "answer": f"Your dataset contains {len(df.columns)} columns.",
            "data": None,
            "chart": False
        }

    if "missing" in q or "null values" in q:

        missing = df.isnull().sum()
        missing = missing[missing > 0]

        if missing.empty:
            answer = "Excellent! Your dataset has no missing values."
        else:
            answer = (
                f"Your dataset has {int(missing.sum())} missing "
                "values across these columns:\n\n"
                + missing.to_string()
            )

        return {
            "answer": answer,
            "data": missing.reset_index(),
            "chart": False
        }

    if any(word in q for word in [
        "duplicate", "duplicates", "repeated", "repeat values"
    ]):

        duplicate_row_count = int(df.duplicated().sum())
        repeated_values = get_duplicate_values(df)

        if not repeated_values.empty:
            answer = (
                f"Your dataset has {duplicate_row_count} completely duplicate rows. "
                f"It also contains repeated values in individual columns."
            )
        elif duplicate_row_count > 0:
            answer = (
                f"Your dataset has {duplicate_row_count} completely duplicate rows."
            )
        else:
            answer = (
                "No completely duplicate rows or repeated values were found."
            )

        if repeated_values.empty:
            return {
                "answer": answer,
                "data": None,
                "chart": False
            }

        return {
            "answer": answer,
            "data": repeated_values,
            "chart": False
        }

    if any(word in q for word in [
        "show columns", "list columns",
        "column names"
    ]):

        return {
            "answer": "Here are the columns in your dataset.",
            "data": pd.DataFrame({
                "Column Names": df.columns
            }),
            "chart": False
        }

    if any(word in q for word in [
        "show data", "show rows", "preview",
        "first rows", "sample data", "head"
    ]):
        return {
            "answer": "Here is a preview of your dataset.",
            "data": df.head(100),
            "chart": False
        }

    if any(word in q for word in [
        "unique values", "distinct values", "list values"
    ]):
        category_col = get_category_column(df, q)
        if category_col:
            values = df[category_col].dropna().drop_duplicates()
            return {
                "answer": f"Unique values in {category_col}:",
                "data": pd.DataFrame({category_col: values}),
                "chart": False
            }

    location_words = [
        "area", "place", "location", "state", "province",
        "country", "city", "district", "region", "zone"
    ]

    if any(word in q for word in location_words):
        location_col, matches = find_location_matches(df, q)

        if location_col is not None and matches is not None:
            locations = matches[location_col].dropna().drop_duplicates()

            if len(locations) == 1:
                return {
                    "answer": (
                        f"The {location_col} is {locations.iloc[0]} "
                        "for the mentioned exam or data."
                    ),
                    "data": matches,
                    "chart": False
                }

            if len(locations) > 1:
                return {
                    "answer": (
                        f"The matching {location_col} values are: "
                        + ", ".join(str(value) for value in locations)
                        + "."
                    ),
                    "data": matches,
                    "chart": False
                }

    # ----------------------------
    # NUMERICAL ANALYSIS
    # ----------------------------

    numeric_col = get_numeric_column(df, q)

    if not numeric_col:

        return {
            "answer": (
                "This dataset has no numerical column for that analysis. "
                "You can ask for a preview, column names, unique values, "
                "missing values, duplicate rows, or identify a category column. "
                f"Available columns: {', '.join(map(str, df.columns))}."
            ),
            "data": None,
            "chart": False
        }

    values = pd.to_numeric(
        df[numeric_col],
        errors="coerce"
    ).dropna()

    if values.empty:

        return {
            "answer": f"No valid numerical values were found in {numeric_col}.",
            "data": None,
            "chart": False
        }

    # ----------------------------
    # ACCURACY QUESTION PRIORITY
    # ----------------------------

    accuracy_columns = [
        column for column in df.columns
        if "accuracy" in str(column).lower()
        or "accurate" in str(column).lower()
    ]

    if "accuracy" in q and accuracy_columns:
        accuracy_col = accuracy_columns[0]
        accuracy_values = pd.to_numeric(
            df[accuracy_col], errors="coerce"
        ).dropna()

        if not accuracy_values.empty:

            def format_accuracy(value):
                numeric_value = float(value)
                if 0 <= numeric_value <= 1:
                    return f"{numeric_value * 100:.2f}%"
                return f"{numeric_value:,.2f}"

            if any(word in q for word in [
                "highest", "maximum", "max", "largest", "most", "best", "top"
            ]):
                idx = accuracy_values.idxmax()
                row = df.loc[[idx]].iloc[0]
                label_col = get_label_column(df, q)

                if label_col:
                    answer = (
                        f"The highest accuracy is in {row[label_col]}, "
                        f"with {accuracy_col} = "
                        f"{format_accuracy(row[accuracy_col])}."
                    )
                else:
                    answer = (
                        f"The highest {accuracy_col} is "
                        f"{format_accuracy(accuracy_values.max())}."
                    )

                return {
                    "answer": answer,
                    "data": df.loc[[idx]],
                    "chart": False
                }

            if any(word in q for word in [
                "lowest", "minimum", "min", "smallest", "least", "worst"
            ]):
                idx = accuracy_values.idxmin()
                row = df.loc[[idx]].iloc[0]
                label_col = get_label_column(df, q)

                if label_col:
                    answer = (
                        f"The lowest accuracy is in {row[label_col]}, "
                        f"with {accuracy_col} = "
                        f"{format_accuracy(row[accuracy_col])}."
                    )
                else:
                    answer = (
                        f"The lowest {accuracy_col} is "
                        f"{format_accuracy(accuracy_values.min())}."
                    )

                return {
                    "answer": answer,
                    "data": df.loc[[idx]],
                    "chart": False
                }

            if any(word in q for word in [
                "average", "mean", "avg", "overall"
            ]):
                return {
                    "answer": (
                        f"The average {accuracy_col} is "
                        f"{format_accuracy(accuracy_values.mean())}."
                    ),
                    "data": None,
                    "chart": False
                }

            if accuracy_values.size == 1:
                return {
                    "answer": (
                        f"The {accuracy_col} is "
                        f"{format_accuracy(accuracy_values.iloc[0])}."
                    ),
                    "data": df[[accuracy_col]],
                    "chart": False
                }

            return {
                "answer": (
                    f"The {accuracy_col} column contains "
                    f"{len(accuracy_values):,} values. "
                    f"Average: {format_accuracy(accuracy_values.mean())}; "
                    f"highest: {format_accuracy(accuracy_values.max())}; "
                    f"lowest: {format_accuracy(accuracy_values.min())}."
                ),
                "data": df[[accuracy_col]].dropna(),
                "chart": False
            }

    # ----------------------------
    # LOCATION / CATEGORY RANKING
    # ----------------------------

    label_col = get_label_column(df, q)

    location_requested = any(word in q for word in [
        "place", "location", "state", "province", "country",
        "city", "district", "region", "area", "zone", "which",
        "where"
    ])

    highest_requested = any(word in q for word in [
        "highest", "maximum", "max", "largest", "most", "best"
    ])

    lowest_requested = any(word in q for word in [
        "lowest", "minimum", "min", "smallest", "least", "worst"
    ])

    rank_requested = "rank" in q or "ranking" in q

    if label_col and (location_requested or rank_requested):

        if rank_requested:
            idx = values.idxmax() if lowest_requested else values.idxmin()
        elif highest_requested:
            idx = values.idxmax()
        elif lowest_requested:
            idx = values.idxmin()
        else:
            idx = values.idxmax()

        row = df.loc[[idx]].iloc[0]
        label_value = row[label_col]
        numeric_value = row[numeric_col]

        if rank_requested:
            phrase = "lowest-ranked" if lowest_requested else "highest-ranked"
        elif lowest_requested:
            phrase = "lowest"
        else:
            phrase = "highest"

        answer = (
            f"The {phrase} {label_col} is {label_value}, "
            f"with {numeric_col} = {numeric_value:,}."
        )

        return {
            "answer": answer,
            "data": df.loc[[idx]],
            "chart": False
        }

    # ----------------------------
    # GROUP BY ANALYSIS
    # ----------------------------

    category_col = get_category_column(df, q)

    group_requested = (
        any(word in q for word in [
            "by", "per", "across", "compare",
            "comparison", "breakdown", "group"
        ])
        or (
            category_col is not None
            and str(category_col).lower() in q
        )
    )

    if category_col and group_requested:

        grouped = (
            df.groupby(category_col, dropna=False)[numeric_col]
            .sum()
            .reset_index()
            .sort_values(numeric_col, ascending=False)
        )

        highest = grouped.iloc[0]

        answer = (
            f"Analysis of {numeric_col} by {category_col}:\n\n"
            f"The highest value is "
            f"{highest[category_col]} with "
            f"{highest[numeric_col]:,.2f}."
        )

        return {
            "answer": answer,
            "data": grouped,
            "chart": True,
            "x": category_col,
            "y": numeric_col
        }

    # ----------------------------
    # TOP N ANALYSIS
    # ----------------------------

    top_match = re.search(r"\btop\s+(\d+)\b", q)

    if top_match and category_col:

        n = min(int(top_match.group(1)), 100)

        grouped = (
            df.groupby(category_col, dropna=False)[numeric_col]
            .sum()
            .reset_index()
            .sort_values(numeric_col, ascending=False)
            .head(n)
        )

        return {
            "answer": (
                f"Here are the top {len(grouped)} "
                f"{category_col} values by {numeric_col}."
            ),
            "data": grouped,
            "chart": True,
            "x": category_col,
            "y": numeric_col
        }

    # ----------------------------
    # HIGHEST / LOWEST ANALYSIS
    # ----------------------------

    if any(word in q for word in [
        "highest", "maximum", "max", "largest",
        "most", "top", "best"
    ]):

        idx = values.idxmax()
        row = df.loc[[idx]]

        return {
            "answer": (
                f"The maximum {numeric_col} is "
                f"{values.max():,.2f}."
            ),
            "data": row,
            "chart": False
        }

    if any(word in q for word in [
        "lowest", "minimum", "min", "smallest",
        "least", "worst"
    ]):

        idx = values.idxmin()
        row = df.loc[[idx]]

        return {
            "answer": (
                f"The minimum {numeric_col} is "
                f"{values.min():,.2f}."
            ),
            "data": row,
            "chart": False
        }

    # ----------------------------
    # TOTAL ANALYSIS
    # ----------------------------

    if any(word in q for word in [
        "total", "sum", "overall"
    ]):

        return {
            "answer": (
                f"The total {numeric_col} is "
                f"{values.sum():,.2f}."
            ),
            "data": pd.DataFrame({
                "Metric": ["Total " + str(numeric_col)],
                "Value": [values.sum()]
            }),
            "chart": False
        }

    # ----------------------------
    # AVERAGE ANALYSIS
    # ----------------------------

    if any(word in q for word in [
        "average", "mean", "avg"
    ]):

        return {
            "answer": (
                f"The average {numeric_col} is "
                f"{values.mean():,.2f}."
            ),
            "data": None,
            "chart": False
        }

    # ----------------------------
    # STATISTICAL SUMMARY
    # ----------------------------

    if any(word in q for word in [
        "statistics", "describe",
        "summary", "distribution"
    ]):

        return {
            "answer": f"Statistical summary of {numeric_col}.",
            "data": values.describe().to_frame(),
            "chart": False
        }

    # ----------------------------
    # ACCURACY ANALYSIS
    # ----------------------------

    accuracy_columns = [
        column for column in df.columns
        if "accuracy" in str(column).lower()
        or "accurate" in str(column).lower()
    ]

    if "accuracy" in q or accuracy_columns:

        accuracy_col = accuracy_columns[0] if accuracy_columns else numeric_col

        if accuracy_col in df.columns:
            accuracy_values = pd.to_numeric(
                df[accuracy_col], errors="coerce"
            ).dropna()

            if not accuracy_values.empty:

                def format_accuracy(value):
                    numeric_value = float(value)
                    if 0 <= numeric_value <= 1:
                        return f"{numeric_value * 100:.2f}%"
                    return f"{numeric_value:,.2f}"

                highest_requested = any(word in q for word in [
                    "highest", "maximum", "max", "largest",
                    "most", "best", "top"
                ])
                lowest_requested = any(word in q for word in [
                    "lowest", "minimum", "min", "smallest",
                    "least", "worst"
                ])

                if highest_requested:
                    idx = accuracy_values.idxmax()
                    label_col = get_label_column(df, q)
                    row = df.loc[[idx]].iloc[0]

                    if label_col:
                        answer = (
                            f"The highest accuracy is in {row[label_col]}, "
                            f"with {accuracy_col} = "
                            f"{format_accuracy(row[accuracy_col])}."
                        )
                    else:
                        answer = (
                            f"The highest {accuracy_col} is "
                            f"{format_accuracy(accuracy_values.max())}."
                        )

                    return {
                        "answer": answer,
                        "data": df.loc[[idx]],
                        "chart": False
                    }

                if lowest_requested:
                    idx = accuracy_values.idxmin()
                    label_col = get_label_column(df, q)
                    row = df.loc[[idx]].iloc[0]

                    if label_col:
                        answer = (
                            f"The lowest accuracy is in {row[label_col]}, "
                            f"with {accuracy_col} = "
                            f"{format_accuracy(row[accuracy_col])}."
                        )
                    else:
                        answer = (
                            f"The lowest {accuracy_col} is "
                            f"{format_accuracy(accuracy_values.min())}."
                        )

                    return {
                        "answer": answer,
                        "data": df.loc[[idx]],
                        "chart": False
                    }

                if any(word in q for word in [
                    "average", "mean", "avg", "overall"
                ]):
                    average_value = accuracy_values.mean()
                    return {
                        "answer": (
                            f"The average {accuracy_col} is "
                            f"{format_accuracy(average_value)}."
                        ),
                        "data": None,
                        "chart": False
                    }

                if "accuracy" in q:
                    if accuracy_values.size == 1:
                        return {
                            "answer": (
                                f"The {accuracy_col} is "
                                f"{format_accuracy(accuracy_values.iloc[0])}."
                            ),
                            "data": df[[accuracy_col]],
                            "chart": False
                        }

                    return {
                        "answer": (
                            f"The {accuracy_col} column contains "
                            f"{len(accuracy_values):,} values. "
                            f"Average: {format_accuracy(accuracy_values.mean())}; "
                            f"highest: {format_accuracy(accuracy_values.max())}; "
                            f"lowest: {format_accuracy(accuracy_values.min())}."
                        ),
                        "data": df[[accuracy_col]].dropna(),
                        "chart": False
                    }

    # ----------------------------
    # FALLBACK
    # ----------------------------

    return {
        "answer": (
            "I couldn't match that question to a supported analysis. "
            "Try mentioning a column name, for example: total [column], "
            "average [column], highest [column], lowest [column], "
            "top 5 [category] by [numeric column], or show unique values. "
            f"Available columns: {', '.join(map(str, df.columns))}."
        ),
        "data": None,
        "chart": False
    }

def find_location_matches(df, question):
    """Find rows whose categorical values match text mentioned in a location question."""

    q = question.lower().strip()

    location_aliases = [
        "place", "location", "state", "province", "country",
        "city", "district", "region", "area", "zone"
    ]

    location_col = None

    for column in df.columns:
        name = str(column).lower()
        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        for alias in location_aliases:
            if alias in name:
                location_col = column
                break

        if location_col is not None:
            break

    if location_col is None:
        return None, None

    for filter_column in df.columns:
        if pd.api.types.is_numeric_dtype(df[filter_column]):
            continue

        if str(filter_column).lower() == str(location_col).lower():
            continue

        for value in df[filter_column].dropna().unique():
            value_text = str(value).strip().lower()

            if len(value_text) < 3:
                continue

            if value_text in q:
                matches = df[df[filter_column].astype(str).str.lower() == value_text]

                if not matches.empty:
                    return location_col, matches

    return location_col, None