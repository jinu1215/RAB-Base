import re

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


country_codes = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT',
     'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL',
     'BM', 'BN', 'BO', 'BQ', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC',
     'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW',
     'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER',
     'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG',
     'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK',
     'HM', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS',
     'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW',
     'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA',
     'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR',
     'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI',
     'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL',
     'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA',
     'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR',
     'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL',
     'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'UZ',
     'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW'
]

class CountryCodeField(forms.CharField):
    default_error_messages = {
        'invalid_country_code': 'Select a valid country code.',
    }

    def validate(self, value):
        super(CountryCodeField, self).validate(value)
        if value and value not in country_codes:
            raise forms.ValidationError(self.error_messages['invalid_country_code'])

    def to_python(self, value):
        if value:
            return value.upper()


class MinLengthValidator(validators.MinLengthValidator):
    message = 'Ensure this value has at least %(limit_value)d elements (it has %(show_value)d).'


class MaxLengthValidator(validators.MaxLengthValidator):
    message = 'Ensure this value has at most %(limit_value)d elements (it has %(show_value)d).'


class CommaSeparatedCharField(forms.Field):
    default_error_messages = {
        'unique': 'There are duplicated values.',
    }

    def __init__(self, unique=False, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.unique, self.dedup, self.max_length, self.min_length = unique, dedup, max_length, min_length
        super(CommaSeparatedCharField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        value = [item.strip() for item in value.split(',') if item.strip()]

        if self.unique:
            for start, obj in enumerate(value):
                for target in value[start + 1:]:
                    if obj == target:
                        raise ValidationError(self.error_messages['unique'])
        else:
            if self.dedup:
                value = list(set(value))

        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value


class CommaSeparatedIntegerField(forms.Field):
    default_error_messages = {
        'invalid': 'Enter comma separated numbers only.',
    }

    def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
        super(CommaSeparatedIntegerField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        try:
            value = [int(item.strip()) for item in value.split(',') if item.strip()]
            if self.dedup:
                value = list(set(value))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])

        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value
