

![Djshop](resources/images/logos/logo.png)


Test shop in Django.

# What's this?

Djshop is a test shop made in Django. To serve as an example of [django-virtual-pos](https://github.com/intelligenia/django-virtual-pos) package

Do not use in production!

# Installation

## Set up virtualenv
````sh
$ cd djshop # move to the root of the repository
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r src/requirements.txt
````

## Local settings

Create a file settings_local.py in **/src/djshop/settings_local.py** with this structure:

````python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xxx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]

DATABASES = {
    'default': {
        'ENGINE': '<your django db backend>',
        'NAME': '<djshop database>',
        'USER': '<djshop database user>',
        'PASSWORD': '<djshop database password>',
        'HOST': '',
        'PORT': ''
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Europe/Madrid"

EMAIL_USE_TLS = True
EMAIL_HOST = '<email host>'
EMAIL_PORT = <email host port>
EMAIL_HOST_USER = '<user email>'
EMAIL_HOST_PASSWORD = '<user email password>'
DEFAULT_FROM_EMAIL = '<default from email>'
````

## Create a superuser

````python
python src/manage.py createsuperuser
````

Use this superuser to manage the shop.

# Standard VPOS payment integration summary

## Requirements

### Required attributes in your sale model

* **operation_number**: will containe the VPOS generated operation number.
* **code**: internal code of that sale in your system.
* **status**: sale status. Only statuses with "pending" value can be paid.

### Required methods in your sale model

* **online_confirm**: mark the sale as paid successfully.


## Sale summary

Include this code in your HEAD section

```html
{% load djangovirtualpos_js %}
{% url 'public:set_payment_attributes' as set_payment_attributes_url %}
{% include_djangovirtualpos_set_payment_attributes_js set_payment_attributes_url sale.code url_ok url_nok %}
```

Include all virtual point of sale buttons you want, e. g.:

```html
{% for virtual_point_of_sale in virtual_point_of_sales %}
    <form>
        <button class="pay_button" data-id="{{virtual_point_of_sale.id}}">
            {{virtual_point_of_sale.name}}
        </button>
    </form>
{% endfor %}
```

Configure the your set_payment_attributes_view:

```python
from djshop.apps.sale.models import Sale
from djangovirtualpos import views as djangovirtualpos_views


def set_payment_attributes(request):
    sale_model = Sale
    sale_ok_url = "public:sale_ok"
    sale_nok_url = "public:sale_cancel"
    return djangovirtualpos_views.set_payment_attributes(request, sale_model, sale_ok_url, sale_nok_url)
```

## Sale confirmation

# Confirm sale

Configure your payment confirmation view. Remember that this view will call **sale.online_confirm()**.

```python
from djshop.apps.sale.models import Sale
from djangovirtualpos import views as djangovirtualpos_views


def confirm_sale(request, virtualpos_type):
    """
    This view will be called by the bank.
    """
    return djangovirtualpos_views.confirm_payment(request, virtualpos_type, Sale)
```

# VPOS payment by reference integration summary

VPOS payment by reference uses an unique reference to make payments without having to
 ask the credic card number

If your REDSYS VPOS allow this (currently only supported by **REDSYS with POST confirmation**),
you only have to

Checkout the club application form more information. The process is defined as follows:

- Administrators create a new member.
- They make a 0€ payment operation (need his/her credit number, CVV and expiration date).
- This operation returns a reference and automatically it is stored in that member.
- From now on, an admin can make direct payments using his/her reference.

# Legal notice

The license of this project is [MIT](LICENSE) and the logos have been created with [Mark Maker](http://emblemmatic.org/markmaker).


# Questions? Suggestions?

Don't hesitate to contact me, write me to diegojREMOVETHISromeroREMOVETHISlopez@REMOVETHISgmail.REMOVETHIScom.

(remove REMOVETHIS to see the real email address)