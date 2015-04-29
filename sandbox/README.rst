1. Change directory to the sandbox directory
2. ``pip install -r requirements.txt``
3. ``python manage.py syncdb``
4. ``python manage.py migrate``
5. ``python manage.py loaddata fixtures/countries.json``

   The countries.json bundled with this project is different from the one
   in oscar in that it sets is_shipping_country to True for all countries,
   otherwise because of the validation we do for shipping addresses gotten
   from Amazon you would get an error message for all countries except GB.
   
6. ``python manage.py oscar_import_catalogue fixtures/catalogue.csv``
7. ``python manage.py collectstatic``
8. Create the image_not_found.jpg file:
   
   ``ln -s /<INSERT PATH TO OSCAR>/static/oscar/img/image_not_found.jpg public/media/``


**Rememeber: Amazon Payments requires your "Allowed JavaScript origin" (one of
the settings when you're setting up your Amazon Payments account) to be a HTTPS URL,
so you will not be able to test the Amazon Payments functionality with a site
run using Django runserver.**
