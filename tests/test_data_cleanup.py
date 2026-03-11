"""
Unit tests for wingbrace.data_cleanup module.
"""

import unittest

from wingbrace.data_cleanup.data_cleaner import DataCleaner
from wingbrace.data_cleanup.data_transformer import DataTransformer
from wingbrace.data_cleanup.data_validator import DataValidator


# ---------------------------------------------------------------------------
# DataCleaner
# ---------------------------------------------------------------------------

class TestDataCleaner(unittest.TestCase):

    def _sample(self):
        return [
            {"name": "  Alice ", "age": "29", "score": None,  "city": "NY"},
            {"name": "Bob",       "age": "NaN", "score": "88.5","city": "LA"},
            {"name": "  Alice ", "age": "29",  "score": None,  "city": "NY"},
            {"name": "Carol",     "age": "35",  "score": "72.0","city": "ny"},
        ]

    def test_strip_whitespace(self):
        data = [{"name": "  Alice "}]
        result = DataCleaner(data).strip_whitespace().get()
        self.assertEqual(result[0]["name"], "Alice")

    def test_fill_missing_none(self):
        data = [{"val": None}, {"val": 5}]
        result = DataCleaner(data).fill_missing(0).get()
        self.assertEqual(result[0]["val"], 0)
        self.assertEqual(result[1]["val"], 5)

    def test_fill_missing_nan_string(self):
        data = [{"val": "NaN"}, {"val": "N/A"}, {"val": "null"}]
        result = DataCleaner(data).fill_missing(-1).get()
        self.assertTrue(all(r["val"] == -1 for r in result))

    def test_drop_missing_removes_none_rows(self):
        data = [{"a": 1, "b": None}, {"a": 2, "b": 3}]
        result = DataCleaner(data).drop_missing().get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["a"], 2)

    def test_drop_duplicates(self):
        result = DataCleaner(self._sample()).strip_whitespace().drop_duplicates().get()
        names = [r["name"] for r in result]
        self.assertEqual(len(result), 3)
        self.assertIn("Alice", names)

    def test_coerce_types_int(self):
        data = [{"age": "25"}, {"age": "30"}]
        result = DataCleaner(data).coerce_types({"age": int}).get()
        self.assertIsInstance(result[0]["age"], int)
        self.assertEqual(result[1]["age"], 30)

    def test_coerce_types_float(self):
        data = [{"score": "88.5"}]
        result = DataCleaner(data).coerce_types({"score": float}).get()
        self.assertIsInstance(result[0]["score"], float)

    def test_coerce_types_invalid_null(self):
        data = [{"age": "abc"}]
        result = DataCleaner(data).coerce_types({"age": int}, on_error="null").get()
        self.assertIsNone(result[0]["age"])

    def test_coerce_types_invalid_raise(self):
        data = [{"age": "abc"}]
        with self.assertRaises((ValueError, TypeError)):
            DataCleaner(data).coerce_types({"age": int}, on_error="raise").get()

    def test_clamp(self):
        data = [{"v": -5}, {"v": 50}, {"v": 200}]
        result = DataCleaner(data).clamp("v", min_val=0, max_val=100).get()
        self.assertEqual(result[0]["v"], 0.0)
        self.assertEqual(result[1]["v"], 50.0)
        self.assertEqual(result[2]["v"], 100.0)

    def test_drop_out_of_range(self):
        data = [{"v": 1}, {"v": 10}, {"v": 100}]
        result = DataCleaner(data).drop_out_of_range("v", min_val=5, max_val=50).get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["v"], 10)

    def test_normalise_case_lower(self):
        data = [{"city": "New York"}, {"city": "LOS ANGELES"}]
        result = DataCleaner(data).normalise_case("lower", fields=["city"]).get()
        self.assertEqual(result[0]["city"], "new york")
        self.assertEqual(result[1]["city"], "los angeles")

    def test_rename_fields(self):
        data = [{"old_name": "Alice"}]
        result = DataCleaner(data).rename_fields({"old_name": "name"}).get()
        self.assertIn("name", result[0])
        self.assertNotIn("old_name", result[0])

    def test_drop_fields(self):
        data = [{"a": 1, "b": 2, "c": 3}]
        result = DataCleaner(data).drop_fields(["b", "c"]).get()
        self.assertEqual(list(result[0].keys()), ["a"])

    def test_keep_fields(self):
        data = [{"a": 1, "b": 2, "c": 3}]
        result = DataCleaner(data).keep_fields(["a", "c"]).get()
        self.assertIn("a", result[0])
        self.assertNotIn("b", result[0])

    def test_flag_missing(self):
        data = [{"a": None}, {"a": 1}]
        result = DataCleaner(data).flag_missing().get()
        self.assertTrue(result[0]["_has_missing"])
        self.assertFalse(result[1]["_has_missing"])

    def test_remove_special_characters(self):
        data = [{"name": "Alice!@#"}]
        result = DataCleaner(data).remove_special_characters(fields=["name"]).get()
        self.assertEqual(result[0]["name"], "Alice")

    def test_method_chaining(self):
        data = self._sample()
        result = (
            DataCleaner(data)
            .strip_whitespace(fields=["name"])
            .fill_missing(0, fields=["score"])
            .coerce_types({"score": float})
            .drop_duplicates()
            .get()
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["score"], 0.0)

    def test_count(self):
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        self.assertEqual(DataCleaner(data).count(), 3)

    def test_coerce_bool_true_values(self):
        data = [{"f": "true"}, {"f": "yes"}, {"f": "1"}, {"f": True}]
        result = DataCleaner(data).coerce_types({"f": bool}).get()
        self.assertTrue(all(r["f"] is True for r in result))

    def test_coerce_bool_false_values(self):
        data = [{"f": "false"}, {"f": "no"}, {"f": "0"}]
        result = DataCleaner(data).coerce_types({"f": bool}).get()
        self.assertTrue(all(r["f"] is False for r in result))


# ---------------------------------------------------------------------------
# DataValidator
# ---------------------------------------------------------------------------

class TestDataValidator(unittest.TestCase):

    def _schema(self):
        return {
            "name":  {"type": str, "required": True, "min_length": 1, "max_length": 50},
            "age":   {"type": int, "required": True, "min_value": 0, "max_value": 150},
            "email": {"type": str, "required": False,
                      "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
            "role":  {"type": str, "allowed_values": ["admin", "user", "guest"]},
        }

    def test_valid_record(self):
        data = [{"name": "Alice", "age": 30, "email": "alice@example.com", "role": "admin"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertTrue(result.is_valid)

    def test_missing_required_field(self):
        data = [{"age": 25}]  # missing 'name'
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        field_errors = [e.field for e in result.errors]
        self.assertIn("name", field_errors)

    def test_wrong_type(self):
        data = [{"name": "Alice", "age": "not_int"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any(e.rule == "type" for e in result.errors))

    def test_below_min_value(self):
        data = [{"name": "X", "age": -1}]
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any(e.rule == "min_value" for e in result.errors))

    def test_exceeds_max_value(self):
        data = [{"name": "X", "age": 200}]
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any(e.rule == "max_value" for e in result.errors))

    def test_pattern_valid(self):
        data = [{"name": "X", "age": 25, "email": "user@domain.com"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertTrue(result.is_valid)

    def test_pattern_invalid(self):
        data = [{"name": "X", "age": 25, "email": "not_an_email"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any(e.rule == "pattern" for e in result.errors))

    def test_allowed_values_valid(self):
        data = [{"name": "X", "age": 25, "role": "user"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertTrue(result.is_valid)

    def test_allowed_values_invalid(self):
        data = [{"name": "X", "age": 25, "role": "superadmin"}]
        result = DataValidator(self._schema()).validate(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any(e.rule == "allowed_values" for e in result.errors))

    def test_custom_validator(self):
        schema = {"score": {"custom": lambda v: v % 2 == 0, "custom_message": "Must be even"}}
        data_valid = [{"score": 4}]
        data_invalid = [{"score": 3}]
        self.assertTrue(DataValidator(schema).validate(data_valid).is_valid)
        self.assertFalse(DataValidator(schema).validate(data_invalid).is_valid)

    def test_min_length(self):
        schema = {"code": {"type": str, "min_length": 3}}
        self.assertFalse(DataValidator(schema).validate([{"code": "AB"}]).is_valid)
        self.assertTrue(DataValidator(schema).validate([{"code": "ABC"}]).is_valid)

    def test_max_length(self):
        schema = {"code": {"type": str, "max_length": 5}}
        self.assertFalse(DataValidator(schema).validate([{"code": "TOOLONG"}]).is_valid)

    def test_validate_one(self):
        result = DataValidator(self._schema()).validate_one({"name": "Alice", "age": 25})
        self.assertTrue(result.is_valid)

    def test_errors_for_field(self):
        data = [{"name": "X", "age": 999}]
        result = DataValidator(self._schema()).validate(data)
        age_errors = result.errors_for_field("age")
        self.assertTrue(len(age_errors) > 0)

    def test_invalid_rows_set(self):
        data = [{"name": "Alice", "age": 30}, {"age": -5}]
        result = DataValidator(self._schema()).validate(data)
        self.assertIn(1, result.invalid_rows)

    def test_summary_string(self):
        data = [{"age": -1}]
        result = DataValidator(self._schema()).validate(data)
        s = result.summary()
        self.assertIn("error", s.lower())


# ---------------------------------------------------------------------------
# DataTransformer
# ---------------------------------------------------------------------------

class TestDataTransformer(unittest.TestCase):

    def test_normalise_minmax(self):
        data = [{"v": 0}, {"v": 50}, {"v": 100}]
        result = DataTransformer(data).normalise_minmax(["v"]).get()
        self.assertAlmostEqual(result[0]["v"], 0.0)
        self.assertAlmostEqual(result[2]["v"], 1.0)

    def test_normalise_zscore(self):
        data = [{"v": 10}, {"v": 20}, {"v": 30}]
        result = DataTransformer(data).normalise_zscore(["v"]).get()
        values = [r["v"] for r in result]
        # Mean should be near 0
        self.assertAlmostEqual(sum(values) / len(values), 0.0, places=5)

    def test_one_hot_encode(self):
        data = [{"color": "red"}, {"color": "blue"}, {"color": "green"}]
        result = DataTransformer(data).one_hot_encode("color").get()
        self.assertIn("color_red", result[0])
        self.assertEqual(result[0]["color_red"], 1)
        self.assertEqual(result[0]["color_blue"], 0)
        self.assertNotIn("color", result[0])  # original dropped

    def test_label_encode(self):
        data = [{"grade": "A"}, {"grade": "B"}, {"grade": "C"}]
        result = DataTransformer(data).label_encode("grade").get()
        self.assertIn(result[0]["grade"], [0, 1, 2])

    def test_label_encode_custom_mapping(self):
        data = [{"size": "S"}, {"size": "M"}, {"size": "L"}]
        mapping = {"S": 0, "M": 1, "L": 2}
        result = DataTransformer(data).label_encode("size", mapping=mapping).get()
        self.assertEqual(result[0]["size"], 0)
        self.assertEqual(result[2]["size"], 2)

    def test_bin(self):
        data = [{"age": 5}, {"age": 25}, {"age": 70}]
        result = DataTransformer(data).bin("age", bins=[0, 18, 65, 120],
                                           labels=["child", "adult", "senior"]).get()
        self.assertEqual(result[0]["age_bin"], "child")
        self.assertEqual(result[1]["age_bin"], "adult")
        self.assertEqual(result[2]["age_bin"], "senior")

    def test_extract_date_parts(self):
        data = [{"joined": "2023-06-15T10:30:00"}]
        result = DataTransformer(data).extract_date_parts("joined", parts=["year", "month"]).get()
        self.assertEqual(result[0]["joined_year"], 2023)
        self.assertEqual(result[0]["joined_month"], 6)

    def test_flatten(self):
        data = [{"user": {"name": "Alice", "city": "NY"}}]
        result = DataTransformer(data).flatten("user").get()
        self.assertIn("user_name", result[0])
        self.assertEqual(result[0]["user_name"], "Alice")
        self.assertNotIn("user", result[0])  # original dropped

    def test_add_field(self):
        data = [{"first": "Alice", "last": "Smith"}]
        result = DataTransformer(data).add_field(
            "full_name", lambda r: f"{r['first']} {r['last']}"
        ).get()
        self.assertEqual(result[0]["full_name"], "Alice Smith")

    def test_rename_fields(self):
        data = [{"old": 1}]
        result = DataTransformer(data).rename_fields({"old": "new"}).get()
        self.assertIn("new", result[0])
        self.assertNotIn("old", result[0])

    def test_drop_fields(self):
        data = [{"a": 1, "b": 2}]
        result = DataTransformer(data).drop_fields(["b"]).get()
        self.assertNotIn("b", result[0])

    def test_round_fields(self):
        data = [{"v": 1.23456789}]
        result = DataTransformer(data).round_fields(["v"], decimals=2).get()
        self.assertAlmostEqual(result[0]["v"], 1.23, places=2)

    def test_reorder_fields(self):
        data = [{"c": 3, "a": 1, "b": 2}]
        result = DataTransformer(data).reorder_fields(["a", "b", "c"]).get()
        self.assertEqual(list(result[0].keys())[0], "a")

    def test_count(self):
        data = [{"x": i} for i in range(5)]
        self.assertEqual(DataTransformer(data).count(), 5)


if __name__ == "__main__":
    unittest.main()
