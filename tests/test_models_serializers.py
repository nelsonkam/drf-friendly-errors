from rest_framework.settings import api_settings

from rest_framework_friendly_errors.settings import (
    FRIENDLY_ERROR_CODES, FRIENDLY_FIELD_ERRORS, FRIENDLY_NON_FIELD_ERRORS
)
from tests import BaseTestCase
from tests.serializers import (
    AnotherSnippetModelSerializer, FieldModelSerializer,
    FieldOptionModelSerializer, SnippetModelSerializer,
    ThirdSnippetModelSerializer
)
from tests.utils import run_is_valid


class SnippetModelSerializerTestCase(BaseTestCase):

    def test_serializer_is_valid(self):
        s = SnippetModelSerializer(data=self.data_set)
        self.assertTrue(s.is_valid())

    def test_serializer_invalid(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = SnippetModelSerializer(data=self.data_set)
        self.assertFalse(s.is_valid())

    def test_error_message(self):
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        self.assertFalse(s.errors)

        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        self.assertTrue(s.errors)
        self.assertTrue(type(s.errors), dict)

    def test_error_message_content(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        self.assertEqual(type(s.errors['errors']), dict)
        self.assertTrue(s.errors['errors'])

    def test_boolean_field_error_content(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['BooleanField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('linenos'))
        self.assertEqual(type(s.errors['errors']['linenos']), list)
        self.assertEqual(s.errors['errors']['linenos'][0]['code'], code)

    def test_char_field_error_content(self):
        # Too long string
        self.data_set['title'] = 'Too Long Title For Defined Serializer'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['max_length']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

        # Empty string
        self.data_set['title'] = ''
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['blank']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

        # No data provided
        self.data_set.pop('title')
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['required']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

    def test_choice_field_error_content(self):
        # invalid choice
        self.data_set['language'] = 'brainfuck'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

        # empty string
        self.data_set['language'] = ''
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

        # no data provided
        self.data_set.pop('language')
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['required']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

    def test_decimal_field_error_content(self):
        # invalid
        self.data_set['rating'] = 'text instead of float'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

        # decimal places
        self.data_set['rating'] = 2.99
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['max_decimal_places']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

        # decimal max digits
        self.data_set['rating'] = 222.9
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['max_digits']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

    def test_datetime_field_error_content(self):
        # invalid
        self.data_set['posted_date'] = 'text instead of date'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DateTimeField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('posted_date'))
        self.assertEqual(type(s.errors['errors']['posted_date']), list)
        self.assertEqual(s.errors['errors']['posted_date'][0]['code'], code)

    def test_custom_field_validation_method(self):
        self.data_set['comment'] = 'comment'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        self.assertIsNotNone(s.errors['errors'].get('comment'))
        self.assertEqual(type(s.errors['errors']['comment']), list)
        self.assertEqual(
            s.errors['errors']['comment'][0]['code'], 'validate_comment')

    def test_custom_field_validation_using_validators(self):
        self.data_set['title'] = 'A title'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(
            s.errors['errors']['title'][0]['code'], 'incorrect_title')

    def test_field_dependency_validation(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(SnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_NON_FIELD_ERRORS['invalid']
        self.assertIsNotNone(
            s.errors['errors'].get(api_settings.NON_FIELD_ERRORS_KEY))
        self.assertEqual(
            type(s.errors['errors'][api_settings.NON_FIELD_ERRORS_KEY]), list)
        c = s.errors['errors'][api_settings.NON_FIELD_ERRORS_KEY][0]['code']
        self.assertEqual(c, code)

    def test_error_registration(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(AnotherSnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

    def test_saving_data(self):
        s = SnippetModelSerializer(data=self.data_set)
        s.is_valid()
        s.save()

    def test_saving_invalid_data(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(AnotherSnippetModelSerializer, data=self.data_set)
        with self.assertRaises(AssertionError):
            s.save()

    def test_register_method_in_field_validation(self):
        self.data_set['comment'] = 'small comment'
        s = run_is_valid(ThirdSnippetModelSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['blank']
        self.assertIsNotNone(s.errors['errors'].get('comment'))
        self.assertEqual(type(s.errors['errors']['comment']), list)
        self.assertEqual(s.errors['errors']['comment'][0]['code'], code)


class FieldAndFieldOptionModelSerializerTestCase(BaseTestCase):

    def test_unique_failed_from_nested_serializer(self):
        field_serializer = FieldModelSerializer(data={'label': 'test'})
        self.assertTrue(field_serializer.is_valid())
        field = field_serializer.save()

        field_option_serializer = FieldOptionModelSerializer(
            data={'value': 1}, context={'field': field})
        self.assertTrue(field_option_serializer.is_valid())
        field_option_serializer.save()

        data_set = {'label': 'test', 'options': [{'value': 1}]}
        s = run_is_valid(FieldModelSerializer, data=data_set)
        code = FRIENDLY_ERROR_CODES['unique']
        self.assertIsNotNone(s.errors['errors'])
        self.assertIsNotNone(s.errors['errors'].get('options'))
        self.assertEqual(type(s.errors['errors']['options']), list)
        self.assertEqual(s.errors['errors']['options'][0]['code'], code)
