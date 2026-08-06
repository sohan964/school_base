import logging
import requests
from requests.exceptions import RequestException
from datetime import datetime, timedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BkashAPI:
    def __init__(self, env):
        self.env = env

        self.config = env["ir.config_parameter"].sudo()

        self.base_url = self.config.get_param("school_base.base_url")
        self.username = self.config.get_param("school_base.username")
        self.password = self.config.get_param("school_base.password")
        self.app_key = self.config.get_param("school_base.app_key")
        self.app_secret = self.config.get_param("school_base.app_secret")

    def _post(self, endpoint, headers=None, payload=None):
        """
        Generic POST request to bKash API
        """

        url = f"{self.base_url}{endpoint}"

        if headers is None:
            headers = {}
        headers.setdefault("Content-Type", "application/json")

        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=30,
            )
            _logger.info("=" * 80)
            _logger.info("URL: %s", url)
            _logger.info("Headers: %s", headers)
            _logger.info("Payload: %s", payload)
            _logger.info("Status Code: %s", response.status_code)
            _logger.info("Response: %s", response.text)
            _logger.info("=" * 80)

            response.raise_for_status()

            return response.json()
        
        except RequestException as e:
            _logger.exception("bKash API Error")

            raise UserError(
                f"Unable to connect to bKash.\n\n{e}"
            )

    def grant_token(self):
    
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "username": self.username,
            "password": self.password,
        }
    
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
        }
    
        result = self._post(
            "/tokenized/checkout/token/grant",
            headers=headers,
            payload=payload,
        )
    
        if result.get("statusCode") == "0000":
    
            self.config.set_param(
                "school_base.access_token",
                result.get("id_token"),
            )
    
            self.config.set_param(
                "school_base.refresh_token",
                result.get("refresh_token"),
            )
    
            self.config.set_param(
                "school_base.token_expiry",
                result.get("expires_in"),
            )
    
            self.config.set_param(
                "school_base.token_created_at",
                datetime.utcnow().isoformat(),
            )
    
        return result

    def ensure_access_token(self):
        """
        Returns a valid access token.
        If there is no token or it has expired,
        automatically request a new one.
        """

        access_token = self.config.get_param("school_base.access_token")
        created_at = self.config.get_param("school_base.token_created_at")
        expires_in = self.config.get_param("school_base.token_expiry")

        if access_token and created_at and expires_in:

            created_at = datetime.fromisoformat(created_at)

            expiry_time = created_at + timedelta(seconds=int(expires_in))

            if datetime.utcnow() < expiry_time:
                return access_token

        result = self.grant_token()

        if result.get("statusCode") != "0000":
            raise UserError(result.get("statusMessage"))

        return self.config.get_param("school_base.access_token")

    def create_payment(
        self,
        amount,
        payer_reference,
        merchant_invoice,
        callback_url,
    ):
        """
        Create a new bKash payment session.
        """

        access_token = self.ensure_access_token()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "authorization": access_token,
            "x-app-key": self.app_key,
        }

        payload = {
            "mode": "0011",
            "payerReference": payer_reference,
            "callbackURL": callback_url,
            "amount": str(amount),
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": merchant_invoice,
        }

        return self._post(
            "/tokenized/checkout/create",
            headers=headers,
            payload=payload,
        )

    def execute_payment(self, payment_id):
        """
        Execute a bKash payment after customer returns
        from the hosted checkout.
        """

        access_token = self.ensure_access_token()

        headers = {
            "Accept": "application/json",
            "authorization": access_token,
            "x-app-key": self.app_key,
        }

        payload = {
            "paymentID": payment_id,
        }

        return self._post(
            "/tokenized/checkout/execute",
            headers=headers,
            payload=payload,
        )