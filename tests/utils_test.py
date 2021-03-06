import decimal
import json
import os
import unittest

from httprunner import loader, utils
from httprunner.utils import (
    ensure_file_path_valid,
    ExtendJSONEncoder,
    override_config_variables,
)


class TestUtils(unittest.TestCase):
    def test_set_os_environ(self):
        self.assertNotIn("abc", os.environ)
        variables_mapping = {"abc": "123"}
        utils.set_os_environ(variables_mapping)
        self.assertIn("abc", os.environ)
        self.assertEqual(os.environ["abc"], "123")

    def test_validators(self):
        from httprunner.builtin import comparators

        functions_mapping = loader.load_module_functions(comparators)

        functions_mapping["equal"](None, None)
        functions_mapping["equal"](1, 1)
        functions_mapping["equal"]("abc", "abc")
        with self.assertRaises(AssertionError):
            functions_mapping["equal"]("123", 123)

        functions_mapping["less_than"](1, 2)
        functions_mapping["less_or_equals"](2, 2)

        functions_mapping["greater_than"](2, 1)
        functions_mapping["greater_or_equals"](2, 2)

        functions_mapping["not_equal"](123, "123")

        functions_mapping["length_equal"]("123", 3)
        with self.assertRaises(AssertionError):
            functions_mapping["length_equal"]("123", "3")
        with self.assertRaises(AssertionError):
            functions_mapping["length_equal"]("123", "abc")
        functions_mapping["length_greater_than"]("123", 2)
        functions_mapping["length_greater_or_equals"]("123", 3)

        functions_mapping["contains"]("123abc456", "3ab")
        functions_mapping["contains"](["1", "2"], "1")
        functions_mapping["contains"]({"a": 1, "b": 2}, "a")
        functions_mapping["contained_by"]("3ab", "123abc456")

        functions_mapping["regex_match"]("123abc456", "^123\w+456$")
        with self.assertRaises(AssertionError):
            functions_mapping["regex_match"]("123abc456", "^12b.*456$")

        functions_mapping["startswith"]("abc123", "ab")
        functions_mapping["startswith"]("123abc", 12)
        functions_mapping["startswith"](12345, 123)

        functions_mapping["endswith"]("abc123", 23)
        functions_mapping["endswith"]("123abc", "abc")
        functions_mapping["endswith"](12345, 45)

        functions_mapping["type_match"](580509390, int)
        functions_mapping["type_match"](580509390, "int")
        functions_mapping["type_match"]([], list)
        functions_mapping["type_match"]([], "list")
        functions_mapping["type_match"]([1], "list")
        functions_mapping["type_match"]({}, "dict")
        functions_mapping["type_match"]({"a": 1}, "dict")

    def test_lower_dict_keys(self):
        request_dict = {
            "url": "http://127.0.0.1:5000",
            "METHOD": "POST",
            "Headers": {"Accept": "application/json", "User-Agent": "ios/9.3"},
        }
        new_request_dict = utils.lower_dict_keys(request_dict)
        self.assertIn("method", new_request_dict)
        self.assertIn("headers", new_request_dict)
        self.assertIn("Accept", new_request_dict["headers"])
        self.assertIn("User-Agent", new_request_dict["headers"])

        request_dict = "$default_request"
        new_request_dict = utils.lower_dict_keys(request_dict)
        self.assertEqual("$default_request", request_dict)

        request_dict = None
        new_request_dict = utils.lower_dict_keys(request_dict)
        self.assertEqual(None, request_dict)

    def test_print_info(self):
        info_mapping = {"a": 1, "t": (1, 2), "b": {"b1": 123}, "c": None, "d": [4, 5]}
        utils.print_info(info_mapping)

    def test_sort_dict_by_custom_order(self):
        self.assertEqual(
            list(
                utils.sort_dict_by_custom_order(
                    {"C": 3, "D": 2, "A": 1, "B": 8}, ["A", "D"]
                ).keys()
            ),
            ["A", "D", "C", "B"],
        )

    def test_ensure_file_path_valid(self):
        self.assertEqual(
            ensure_file_path_valid("examples/a-b.c/d f/hardcode.yml"),
            os.path.join(os.getcwd(), "examples/a_b_c/d_f/hardcode.yml"),
        )
        self.assertEqual(
            ensure_file_path_valid("1/2B/3.yml"),
            os.path.join(os.getcwd(), "T1/T2B/T3.yml"),
        )
        self.assertEqual(
            ensure_file_path_valid("examples/a-b.c/2B/hardcode.yml"),
            os.path.join(os.getcwd(), "examples/a_b_c/T2B/hardcode.yml"),
        )
        self.assertEqual(
            ensure_file_path_valid("examples/postman_echo/request_methods/"),
            os.path.join(os.getcwd(), "examples/postman_echo/request_methods"),
        )
        self.assertEqual(
            ensure_file_path_valid(os.path.join(os.getcwd(), "test.yml")),
            os.path.join(os.getcwd(), "test.yml"),
        )
        self.assertEqual(
            ensure_file_path_valid(os.getcwd()), os.getcwd(),
        )
        self.assertEqual(
            ensure_file_path_valid(os.getcwd() + ".csv"), os.getcwd() + ".csv",
        )

    def test_safe_dump_json(self):
        class A(object):
            pass

        data = {"a": A(), "b": decimal.Decimal("1.45")}

        with self.assertRaises(TypeError):
            json.dumps(data)

        json.dumps(data, cls=ExtendJSONEncoder)

    def test_override_config_variables(self):
        step_variables = {"base_url": "$base_url", "foo1": "bar1"}
        config_variables = {"base_url": "https://httpbin.org", "foo1": "bar111"}
        self.assertEqual(
            override_config_variables(step_variables, config_variables),
            {"base_url": "https://httpbin.org", "foo1": "bar1"},
        )
