import unittest
from unittest.mock import patch
from Botc_Code import validate_register

class TestRegisterValidation(unittest.TestCase):
    '''
    Unit testing validate_register() function
    '''
    def test_valid_input(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertTrue(validate_register("ValidUser", "strongpass"))

    def test_empty_username(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("", "password123"))

    def test_empty_password(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", ""))

    def test_username_too_long(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("ThisUsernameIsWayTooLong", "password123"))

    def test_username_invalid_characters(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Invalid!Name", "password123"))

    def test_username_not_alpha(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("User123", "password123"))

    def test_password_too_short(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "pass"))

    def test_password_with_angle_brackets(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "pass<word"))

    def test_password_with_space(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", "my pass"))

    def test_username_already_exists(self):
        with patch('Botc_Code.checkUsername', return_value=True):
            self.assertFalse(validate_register("ExistingUser", "securePass"))

    def test_non_string_username(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register(12345, "password123"))

    def test_non_string_password(self):
        with patch('Botc_Code.checkUsername', return_value=False):
            self.assertFalse(validate_register("Username", 987654321))



if __name__ == "__main__":
    unittest.main()