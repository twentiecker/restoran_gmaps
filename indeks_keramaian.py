import json
import pandas as pd
from datetime import date


class IndeksKeramaian:
    # get date today
    today = date.today()
    formatted_today = today.strftime("%d-%m-%Y")

    # Load the JSON data
    with open(f"restaurants_{formatted_today}.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Function to calculate the busyness index for each restaurant
    def calculate_busyness_index(busy_times):
        total_busy_score = 0
        hour_count = 0

        for day, hours in busy_times.items():
            for hour, busy_score in hours.items():
                total_busy_score += busy_score
                hour_count += 1

        if hour_count == 0:
            return 0  # To avoid division by zero if no data is available

        return total_busy_score / hour_count

    # Add the busyness index to each restaurant
    for restaurant_name, details in data.items():
        if "busy_times" in details:
            busy_times = details["busy_times"]
            details["busyness_index"] = calculate_busyness_index(busy_times)

    # Save the updated data back to a JSON file with the busyness index
    with open(
        f"restaurants_with_busyness_index_{formatted_today}.json", "w", encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=4)

    print(
        f"Data has been successfully exported to restaurants_with_busyness_index_{formatted_today}.json"
    )

    # Process data and create a list for DataFrame
    restaurants_list = []
    for restaurant_name, details in data.items():
        entry = {
            "name": restaurant_name,
            "rating": details.get("rating"),
            "reviews": details.get("reviews"),
            "price": details.get("price"),
            "category": details.get("category"),
            "address": details.get("address"),
            "website": details.get("website"),
            "phone": details.get("phone"),
            "busyness_index": (
                calculate_busyness_index(details["busy_times"])
                if "busy_times" in details
                else None
            ),
        }
        restaurants_list.append(entry)

    # Convert the list to a DataFrame
    df = pd.DataFrame(restaurants_list)

    # Export to Excel
    df.to_excel(f"restaurants_with_busyness_index_{formatted_today}.xlsx", index=False)

    print(
        f"Data has been successfully exported to restaurants_with_busyness_index_{formatted_today}.xlsx"
    )
