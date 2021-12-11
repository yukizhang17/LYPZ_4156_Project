import unittest
import os
import sys
import uuid

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

try:
    from application_services.user_services import login_request, \
        signup_request, validate_token, get_user_id, valid_email, \
        validate_all_api_form_fields
except Exception:
    raise


class Test_TestUserServices(unittest.TestCase):

    # Testcase 1:
    def test_validate_all_fields(self):
        form = {}
        requirement = []

        self.assertTrue(validate_all_api_form_fields(requirement, form))

        requirement.append("user")
        self.assertFalse(validate_all_api_form_fields(requirement, form))

        form["user"] = "4156"
        self.assertTrue(validate_all_api_form_fields(requirement, form))
        
        # Testcase 6:
    def test_check_email(self):
        self.assertFalse(valid_email(""))
        self.assertFalse(valid_email("asdasd"))
        self.assertFalse(valid_email("asdadad@"))
        self.assertFalse(valid_email("dededad@gmail"))
        self.assertTrue(valid_email("asdad@gmail.com"))
        self.assertTrue(valid_email("daioda@columbia.edu"))

    # Testcase 2:
    def test_signup_request(self):
        email = uuid.uuid4().hex
        user_email = email + "@columbia.edu"
        user_password = "LYPZ4156"

        self.assertTrue("_id" in signup_request(
            user_email,
            user_password
            ).json())
        self.assertTrue(signup_request(
            user_email,
            user_password
            ).json()["statusCode"] == 400)

        application_email = email + "@gmail.com"

        application_password = "LYPZ4156"

        api_key = "6f074b5f90a147e78988ca4ee373191f"

        

        self.assertTrue("_id" in signup_request(
            application_email,
            application_password,
            api_key).json()
            )


    # Testcase 3:
    def test_login_request(self):
        username = 'jonathan.jsliu@gmail.com_' + \
                    'apikey_6f074b5f90a147e78988ca4ee373191f'
        user_password = "LYPZ4156"

        self.assertTrue("access_token" in login_request(
            username,
            user_password
            ))

        user_password = "LYPZ4155"

        self.assertTrue(login_request(
            username,
            user_password
            )['status_code'] == "403")

    # Testcase 4:
    def test_validate_token(self):
        email = uuid.uuid4().hex + "@columbia.edu"
        password = "LYPZ4156"
        api_key = "6f074b5f90a147e78988ca4ee373191f"
        username = email + "_apikey_" + api_key

        signup_request(email, password, api_key)
        access_token = login_request(username, password)["access_token"]

        self.assertTrue("sub" in validate_token(access_token))

        access_token = access_token[0:-1]

        self.assertTrue('status_code' in validate_token(access_token))

    # Testcase 5:
    def test_get_user_id(self):
        email = uuid.uuid4().hex + "@columbia.edu"
        password = "LYPZ4156"
        api_key = "6f074b5f90a147e78988ca4ee373191f"
        username = email + "_apikey_" + api_key

        id = signup_request(email, password, api_key).json()["_id"]
        access_token = login_request(username, password)["access_token"]

        self.assertTrue(get_user_id(access_token) == id)
        self.assertFalse(get_user_id(access_token[0:-1]))




if __name__ == '__main__':
    unittest.main()
