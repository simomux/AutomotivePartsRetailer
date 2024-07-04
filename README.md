# Project for my Web Technologies exam A.Y. 2023/2024
## Summary
This web app is designed to help local car parts retailers reach more clients via e-commerce.

An unregistered user can visit the e-commerce site but cannot order anything unless they register first.

A registered user can add items to their shopping cart and make an order after choosing a method of payment and specifying shipping details.

The owner of the shop manages orders and prepares them for shipping.

Once an order is shipped, a notification is sent to the user, informing them of the shipment and specifying the expected delivery date.

## How to run

After cloning the repo make sure that [pipenv](https://pypi.org/project/pipenv/) is installed.

To create the venv and install the dependencies, run in the project directory:
```bash
pipenv install
pipenv shell
```

After that, create the DB with:
```bash
python3 manage.py migrate
```

If you want to populate the database you can modify [urls.py](https://github.com/simomux/AutomotivePartsRetailer/blob/a92222bb13e06f7b919761a11cd7b98ad2d5ec61/AutomotivePartsRetailer/urls.py) by uncommenting the `init_db()` function call

Then you can start project with:
```bash
python3 -m manage runserver 8080
```

Some fictional accounts have been created for testing purposes, you can look up the credentials in [initcmds.py](https://github.com/simomux/AutomotivePartsRetailer/blob/a92222bb13e06f7b919761a11cd7b98ad2d5ec61/AutomotivePartsRetailer/initcmds.py)

If you want to clean and repopulate the DB, just uncomment `erase_db()` in [urls.py](https://github.com/simomux/AutomotivePartsRetailer/blob/a92222bb13e06f7b919761a11cd7b98ad2d5ec61/AutomotivePartsRetailer/urls.py) and rerun the project.