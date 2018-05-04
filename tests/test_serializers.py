from rest_framework import serializers
from rest_framework.settings import api_settings

from rest_framework_friendly_errors.mixins import (
    RestValidationError, SerializerErrorMessagesMixin
)
from rest_framework_friendly_errors.settings import (
    FRIENDLY_FIELD_ERRORS, FRIENDLY_NON_FIELD_ERRORS
)

from . import BaseTestCase
from .serializers import (
    FieldsErrorAsDictInValidateSerializer, NonFieldErrorAsStringSerializer,
    NonFieldErrorAsStringWithCodeSerializer, RegisterMixErrorSerializer,
    RegisterMultipleFieldsErrorSerializer, RegisterSingleFieldErrorSerializer,
    SnippetSerializer, SnippetValidator
)
from .utils import run_is_valid


class SimpleSerializerClass(SerializerErrorMessagesMixin,
                            serializers.Serializer):
    text_field = serializers.CharField(max_length=255)
    integer_field = serializers.IntegerField()
    boolean_field = serializers.BooleanField(default=True)


class SanityTestCase(BaseTestCase):

    def test_serializer_valid(self):
        s = SimpleSerializerClass(data={'text_field': 'TEST',
                                        'integer_field': 0,
                                        'boolean_field': False})
        self.assertTrue(s.is_valid())

    def test_serializer_invalid(self):
        s = SimpleSerializerClass(data={'text_field': 'TEST',
                                        'integer_field': 'TEST',
                                        'boolean_field': False})
        self.assertFalse(s.is_valid())


class SerializerErrorsTestCase(BaseTestCase):

    def test_serializer_is_valid(self):
        s = SnippetSerializer(data=self.data_set)
        self.assertTrue(s.is_valid())

    def test_serializer_invalid(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = SnippetSerializer(data=self.data_set)
        self.assertFalse(s.is_valid())

    def test_error_message(self):
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        self.assertFalse(s.errors)

        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        self.assertTrue(s.errors)
        self.assertTrue(type(s.errors), dict)

    def test_error_message_content(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        self.assertEqual(type(s.errors['errors']), dict)
        self.assertTrue(s.errors['errors'])

    def test_boolean_field_error_content(self):
        self.data_set['linenos'] = 'A text instead of a bool'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['BooleanField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('linenos'))
        self.assertEqual(type(s.errors['errors']['linenos']), list)
        self.assertEqual(s.errors['errors']['linenos'][0]['code'], code)

    def test_char_field_error_content(self):
        # Too long string
        self.data_set['title'] = 'Too Long Title For Defined Serializer'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['max_length']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

        # Empty string
        self.data_set['title'] = ''
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['blank']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

        # No data provided
        self.data_set.pop('title')
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['CharField']['required']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

    def test_choice_field_error_content(self):
        # invalid choice
        self.data_set['language'] = 'brainfuck'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

        # empty string
        self.data_set['language'] = ''
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

        # no data provided
        self.data_set.pop('language')
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['required']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

    def test_decimal_field_error_content(self):
        # invalid
        self.data_set['rating'] = 'text instead of float'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

        # decimal places
        self.data_set['rating'] = 2.99
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['max_decimal_places']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

        # decimal max digits
        self.data_set['rating'] = 222.9
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DecimalField']['max_digits']
        self.assertIsNotNone(s.errors['errors'].get('rating'))
        self.assertEqual(type(s.errors['errors']['rating']), list)
        self.assertEqual(s.errors['errors']['rating'][0]['code'], code)

    def test_datetime_field_error_content(self):
        # invalid
        self.data_set['posted_date'] = 'text instead of date'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['DateTimeField']['invalid']
        self.assertIsNotNone(s.errors['errors'].get('posted_date'))
        self.assertEqual(type(s.errors['errors']['posted_date']), list)
        self.assertEqual(s.errors['errors']['posted_date'][0]['code'], code)

    def test_custom_field_validation_method(self):
        self.data_set['comment'] = 'comment'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        self.assertIsNotNone(s.errors['errors'].get('comment'))
        self.assertEqual(type(s.errors['errors']['comment']), list)
        self.assertEqual(s.errors['errors']['comment'][0]['code'],
                         'validate_comment')

    def test_custom_field_validation_using_validators(self):
        self.data_set['title'] = 'A title'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'],
                         'incorrect_title')

    def test_field_dependency_validation(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(SnippetSerializer, data=self.data_set)
        code = FRIENDLY_NON_FIELD_ERRORS['invalid']
        self.assertIsNotNone(
            s.errors['errors'].get(api_settings.NON_FIELD_ERRORS_KEY))
        self.assertEqual(
            type(s.errors['errors'][api_settings.NON_FIELD_ERRORS_KEY]), list)
        c = s.errors['errors'][api_settings.NON_FIELD_ERRORS_KEY][0]['code']
        self.assertEqual(c, code)

    def test_single_field_error_registration(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(RegisterSingleFieldErrorSerializer,
                         data=self.data_set)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        self.assertEqual(s.errors['errors']['language'][0]['code'], code)

    def test_multiple_fields_error_registration(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(RegisterMultipleFieldsErrorSerializer,
                         data=self.data_set)

        self.assertIsNotNone(s.errors['errors'].get('language'))
        self.assertEqual(type(s.errors['errors']['language']), list)
        code = FRIENDLY_FIELD_ERRORS['ChoiceField']['invalid_choice']
        c = s.errors['errors']['language'][0]['code']
        self.assertEqual(c, code)

        self.assertIsNotNone(s.errors['errors'].get('linenos'))
        self.assertEqual(type(s.errors['errors']['linenos']), list)
        code = FRIENDLY_FIELD_ERRORS['BooleanField']['invalid']
        c = s.errors['errors']['linenos'][0]['code']
        self.assertEqual(c, code)

    def test_mix_errors_registration(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(RegisterMixErrorSerializer, data=self.data_set)

        errors = s.errors['errors']

        self.assertIsNotNone(errors.get(api_settings.NON_FIELD_ERRORS_KEY))
        self.assertEqual(type(errors[api_settings.NON_FIELD_ERRORS_KEY]), list)
        c = errors[api_settings.NON_FIELD_ERRORS_KEY][0]['code']
        self.assertEqual(c, 'custom_code')

        self.assertIsNotNone(s.errors['errors'].get('linenos'))
        self.assertEqual(type(s.errors['errors']['linenos']), list)
        code = FRIENDLY_FIELD_ERRORS['BooleanField']['invalid']
        c = s.errors['errors']['linenos'][0]['code']
        self.assertEqual(c, code)

    def test_non_field_error_as_string(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(NonFieldErrorAsStringSerializer,
                         data=self.data_set)
        errors = s.errors['errors'].get(api_settings.NON_FIELD_ERRORS_KEY)
        self.assertIsNotNone(errors)
        self.assertEqual(type(errors), list)
        self.assertEqual(errors[0]['message'], 'Test')
        code = FRIENDLY_NON_FIELD_ERRORS['invalid']
        self.assertEqual(errors[0]['code'], code)

    def test_non_field_error_as_string_with_custom_error_code(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(NonFieldErrorAsStringWithCodeSerializer,
                         data=self.data_set)
        errors = s.errors['errors'].get(api_settings.NON_FIELD_ERRORS_KEY)
        self.assertIsNotNone(errors)
        self.assertEqual(type(errors), list)
        self.assertEqual(errors[0]['message'], 'Test')
        self.assertEqual(errors[0]['code'], 'custom_code')

    def test_non_field_error_as_dict(self):
        self.data_set['title'] = 'A Python'
        self.data_set['language'] = 'c++'
        s = run_is_valid(FieldsErrorAsDictInValidateSerializer,
                         data=self.data_set)
        errors = s.errors['errors']

        self.assertIsNotNone(errors.get('title'))
        self.assertEqual(type(errors['title']), list)
        self.assertEqual(errors['title'][0]['code'], 'custom_code')
        self.assertEqual(errors['title'][0]['message'], 'not good')

        self.assertIsNotNone(errors.get('linenos'))
        self.assertEqual(type(errors['linenos']), list)
        self.assertEqual(errors['linenos'][0]['code'], 'invalid')
        self.assertEqual(errors['linenos'][0]['message'], 'not good')

        self.assertIsNotNone(errors.get('language'))
        self.assertEqual(type(errors['language']), list)
        self.assertEqual(errors['language'][0]['code'], 'invalid')
        self.assertEqual(errors['language'][0]['message'], 'not good')

    def test_failed_relation_lookup(self):
        s = run_is_valid(SnippetValidator, data={'title': 'invalid'})
        code = FRIENDLY_FIELD_ERRORS['SlugRelatedField']['does_not_exist']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

    def test_failed_relation_lookup_many_to_many(self):
        data = {'title': ['another', 'invalid']}
        s = run_is_valid(SnippetValidator, data=data)
        code = FRIENDLY_FIELD_ERRORS['SlugRelatedField']['does_not_exist']
        self.assertIsNotNone(s.errors['errors'].get('title'))
        self.assertEqual(type(s.errors['errors']['title']), list)
        self.assertEqual(s.errors['errors']['title'][0]['code'], code)

    def test_error_registration_misc(self):
        def error_key(m, c):
            return '%s_%s' % (m, c)

        # no `field_name` and `error_code`
        with self.assertRaises(ValueError) as e:
            s = SnippetValidator()
            s.register_error('test')
        self.assertEqual(str(e.exception),
                         'For non field error you must provide an error code')

        # with `error_code` (non field error)
        s = SnippetValidator()
        with self.assertRaises(RestValidationError):
            message = 'test'
            error_code = 'invalid'
            s.register_error(message, error_code=error_code)
        errors = s.registered_errors.get(api_settings.NON_FIELD_ERRORS_KEY)
        self.assertIsNotNone(errors)
        error = errors[0].get(error_key(message, error_code))
        self.assertIsNotNone(error)
        self.assertEqual(error[0].get('message'), message)
        self.assertEqual(error[0].get('code'), error_code)

        # invalid `field_name`
        with self.assertRaises(ValueError) as e:
            s = SnippetValidator()
            s.register_error('test', field_name='invalid')
        self.assertEqual(str(e.exception), 'Incorrect field name: invalid')

        # with valid `field_name` but no `error_key` and `error_code`
        with self.assertRaises(ValueError) as e:
            s = SnippetValidator()
            s.register_error('test', field_name='title')
        self.assertEqual(str(e.exception),
                         'You have to provide either error key or error code')

        # with `field_name` and `error_code`
        s = SnippetValidator()
        with self.assertRaises(RestValidationError):
            message = 'test'
            field_name = 'title'
            error_code = 'invalid'
            s.register_error(message,
                             field_name=field_name,
                             error_code=error_code)
        error = s.registered_errors.get(field_name)
        self.assertIsNotNone(error)
        self.assertEqual(error[0].get('message'), message)
        self.assertEqual(error[0].get('code'), error_code)

        # with valid `field_name` but invalid `error_key`
        with self.assertRaises(ValueError) as e:
            s = SnippetValidator()
            s.register_error('test', field_name='title', error_key='ohh_no')
        self.assertGreater(str(e.exception).find('Unknown error key'), -1)

        # with `field_name` and `error_code` and `meta`
        s = SnippetValidator()
        with self.assertRaises(RestValidationError):
            message = 'test'
            field_name = 'title'
            error_code = 'invalid'
            meta = [1]
            s.register_error(message,
                             field_name=field_name,
                             error_code=error_code,
                             meta=meta)
        error = s.registered_errors.get(field_name)
        self.assertIsNotNone(error)
        self.assertEqual(error[0].get('message'), message)
        self.assertEqual(error[0].get('code'), error_code)
        self.assertEqual(error[0].get('meta'), meta)
