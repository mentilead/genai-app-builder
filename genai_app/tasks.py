import requests
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.utils import IntegrityError


from core.models import CustomUser, Organization
from genaiappbuilder.celery import app

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'accept': 'application/json'})
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        return response.json()


@app.task
def sync_lite_llm_user(user_id: int):
    try:
        api_client = ApiClient(settings.LITE_LLL_BASE_URL, settings.LITE_LLM_API_KEY)
        custom_user = CustomUser.objects.get(id=user_id)

        data = {
            'user_id': f'{user_id}',
            'auto_create_key': custom_user.lite_llm_api_key is None
        }

        try:
            if custom_user.lite_llm_api_key is None:
                response = api_client.post('user/new', data=data)
                logger.info(f"New user created {user_id}")
            else:
                response = api_client.post('user/update', data=data)
                logger.info(f"User updated {user_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return

        if custom_user.lite_llm_api_key is None:
            if 'key' not in response:
                logger.error("Response from API does not contain 'key'")
                return

            custom_user.lite_llm_api_key = response['key']
            custom_user.save()

    except User.DoesNotExist:
        logger.error(f"User does not exist: {user_id}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


@app.task
def make_api_call(endpoint, method="GET", params=None):
    api_client = ApiClient(settings.LITE_LLL_BASE_URL, settings.LITE_LLM_API_KEY)
    response = api_client.get(endpoint, params=params)
    return response  # This result can be used by the callback


@app.task
def process_response(result):
    # This task will process the result of the make_api_call task
    # TODO: write your processing logic here
    print('Processing result:', result)

