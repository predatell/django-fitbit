from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

from . import defaults
from .models import UserFitbit


def create_fitbit(consumer_key=None, consumer_secret=None, **kwargs):
    """Shortcut to create a Fitbit instance.

    If consumer_key or consumer_secret are not provided, then the values
    specified in settings are used.
    """
    if consumer_key is None:
        consumer_key = getattr(settings, 'FITAPP_CONSUMER_KEY', None)
    if consumer_secret is None:
        consumer_secret = getattr(settings, 'FITAPP_CONSUMER_SECRET', None)

    if consumer_key is None or consumer_secret is None:
        raise ImproperlyConfigured("Consumer key and consumer secret cannot "
                "be null, and must be explicitly specified or set in your "
                "Django settings")

    return Fitbit(consumer_key=consumer_key, consumer_secret=consumer_secret,
            **kwargs)


def is_integrated(user):
    """Returns True if we have Oauth info for the user.

    This does not currently require that the token and secret are valid.
    """
    return UserFitbit.objects.filter(user=user).exists()


def get_valid_periods():
    """Returns list of periods for which one may request time series data."""
    return ['1d', '7d', '30d', '1w', '1m', '3m', '6m', '1y', 'max']


def get_fitbit_steps(fbuser, period):
    """Creates a Fitbit API instance and retrieves step data for the period.

    Several exceptions may be thrown:
        ValueError       - Invalid period argument.
        HTTPUnauthorized - 401 - fbuser has bad authentication credentials.
        HTTPForbidden    - 403 - This isn't specified by Fitbit, but does
                                 appear in the Python Fitbit library.
        HTTPNotFound     - 404 - The specific resource doesn't exist.
        HTTPConflict     - 409 - Usually a rate limit issue.
        HTTPServerError  - >=500 - Fitbit server error or maintenance.
        HTTPBadRequest   - >=400 - Bad request.
    """
    fb = create_fitbit(**fbuser.get_user_data())
    data = fb.time_series('activities/steps', period=period)
    steps = data['activities-steps']
    return steps


def get_integration_template():
    return getattr(settings, 'FITAPP_INTEGRATION_TEMPLATE',
            defaults.FITAPP_INTEGRATION_TEMPLATE)


def get_error_template():
    return getattr(settings, 'FITAPP_ERROR_TEMPLATE',
            defaults.FITAPP_ERROR_TEMPLATE)