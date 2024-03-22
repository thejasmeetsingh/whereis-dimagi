import imaplib
import email
import logging
import requests
from email.header import decode_header

from django.conf import settings
from rest_framework import status as status_codes

from whereis.celery import app
from api.models import Employee, Location
from api.choices import BadgeChoices

logger = logging.getLogger(__name__)


def process_location_data(location_data: dict) -> dict:
    """
    Process the location data coming from Geo Name API
    """

    geo_names = location_data.get("geonames", [])
    if not geo_names:
        return {}

    # Sort the data based on greatest population
    geo_names.sort(key=lambda x: x["population"], reverse=True)

    # Retrieve latitude and longitude, And parse them to float
    lat, lng = float(geo_names[0]["lat"]), float(geo_names[0]["lng"])

    return {
        "name": geo_names[0]["name"],
        "latitude": lat,
        "longitude": lng,
        "link": f"https://www.google.com/maps/{lat},{lng}"
    }


@app.task
def allocate_badges(employee_id: str) -> None:
    """
    Check if the given employee is eligible for a badge
    """

    employee = Employee.objects.get(id=employee_id)
    total_locations = Location.objects.filter(employee_id=employee_id).count()
    badge = BadgeChoices.PLT.value[0]

    if total_locations >= 3:
        badge = BadgeChoices.LLP.value[0]

    if total_locations >= 10:
        badge = BadgeChoices.MLP.value[0]

    Employee.objects.filter(id=employee_id).update(badge=badge)

    logger.info("Badge allocated successfully")


@app.task
def retrieve_and_save_location_details(employee_email: str, location: str) -> None:
    """
    Call Geo Names API to fetch the location details
    And, Save it in DB
    """

    geo_name_api_username = settings.GEO_NAME_API_USERNAME
    url = f"http://api.geonames.org/searchJSON?q={location}&maxRows=10&username={geo_name_api_username}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    location_detail = dict()

    if response.status_code == status_codes.HTTP_200_OK:
        location_detail = process_location_data(response.json())

    if not location_detail:
        location_detail.update({
            "name": location,
            "latitude": None,
            "longitude": None,
            "link": None
        })

    # Get or create employee record
    employee, _ = Employee.objects.get_or_create(
        email=employee_email,
        badge=BadgeChoices.PLT.value[0]
    )

    # Create a location record
    Location.objects.create(
        employee=employee,
        geo_name_api_response=response.json(),
        **location_detail
    )

    # allocate_badges.apply_async(kwargs={"employee_id": str(employee.id)})
    allocate_badges(employee_id=str(employee.id))


@app.task
def fetch_emails() -> None:
    """
    This async task will run once in every 5 minutes,
    And it will: 
    1. Fetch the un-read emails
    2. Process the email data like: sender and subject
    3. Call other utils function for fetching and storing location details in DB
    """

    mailbox = 'inbox'
    username = settings.GOOGLE_USERNAME
    password = settings.GOOGLE_PASSWORD
    server = 'imap.gmail.com'
    allowed_domains = ["gmail.com"]

    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select(mailbox)

    logger.info("Logged in to the mail server successfully")

    status, message_numbers = mail.search(None, 'UNSEEN')
    if status != 'OK':
        logger.error("No new emails to read")
        return

    for num in message_numbers[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        if status != 'OK':
            logger.error("ERROR getting message %s", num.decode('utf-8'))
            return

        msg = email.message_from_bytes(data[0][1])

        # Parse email sender
        from_header = msg["From"]
        sender = email.utils.parseaddr(from_header)[1]

        # Check if the sender's email domain matches the allowed domains
        for allowed_domain in allowed_domains:
            if sender.endswith(f"@{allowed_domain}"):
                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                # retrieve_and_save_location_details.apply_async(kwargs={
                #     "location": subject,
                #     "employee_email": sender
                # })
                retrieve_and_save_location_details(sender, subject)

    mail.close()
    mail.logout()

    logger.info("Email process successfully!")
