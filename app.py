from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

# Function to scrape data from the website using Playwright
def get_phone_data(phone_number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Launch browser in headless mode
        page = browser.new_page()

        # Go to the phone validator website
        page.goto("https://www.phonevalidator.com/")

        # Enter the phone number into the input field
        page.fill('input[name="ctl00$ContentPlaceHolder1$GpofOvnvs"]', phone_number)

        # Click the "Search" button
        page.click('input[name="ctl00$ContentPlaceHolder1$uznevtopsvc"]')

        # Wait for the results page to load
        page.wait_for_load_state("networkidle")

        # Navigate to the results page (This will happen automatically after form submission)
        result_url = "https://www.phonevalidator.com/results.aspx"
        page.goto(result_url)

        # Scrape the required data
        report_date = page.query_selector('#ContentPlaceHolder1_ReportDateLabel').inner_text()
        line_type = page.query_selector('#30162e05-68ab-4bbc-88e4-8e88359258c0').inner_text()
        company = page.query_selector('#fc7031a6-4776-49c4-849a-9c2b09f55ee2').inner_text()
        location = page.query_selector('#5e9a8f3b-b13d-4943-ad2c-36920b7b2c8e').inner_text()

        # Close the browser
        browser.close()

        # Return the scraped data
        return {
            "reportdate": report_date,
            "line_type": line_type,
            "company": company,
            "location": location
        }

# Define the Flask API route
@app.route('/check', methods=['GET'])
def check_phone():
    # Get the phone number from the request parameters
    phone_number = request.args.get('number')

    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    try:
        # Scrape the phone data using the Playwright function
        phone_data = get_phone_data(phone_number)
        return jsonify(phone_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=True)
