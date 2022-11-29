# Opply Assignment by GCardona.

This is my take on resolving the Backend Assignment for Opply.

You can test this by just by navigating to the root and:

```bash
docker-compose up -d
```

Also feel free to run tests by:
```bash
docker-compose run web python manage.py test --noinput
```
### Create a User
```bash
docker-compose exec -it web bash
# Inside the docker container now:
$ ./manage.py createsuperuser
[...] # Follow the prompts.
$ exit
```

## Playing with the API.

I attach here some examples to be done with `curl` to play with the functionality. Otherwise, I strongly recommend trying out [Insomnia](https://insomnia.rest), for which I attach the file `insomnia_opply.json`. Import it into Insomnia and you have everything there to test :)
### Get API Token for the created user `GET /token/`:
```bash
# Outside the container.
curl --request GET \
  --url http://localhost:8000/token/ \
  -u "{username}:{password}"
# Answer:
{"token":"033e4e9652c885c961fc1143eac575794c1b76c8"}
```
Note: We can save this token and use it for the rest of the API calls:

### Create some Products `POST /products/`
```bash
curl --request POST \
  --url http://localhost:8000/products/ \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
  --data '{
	"name": "Product 1",
	"price": "11.11",
	"quantity_in_stock": 10
  }'
  
curl --request POST \
  --url http://localhost:8000/products/ \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
  --data '{
	"name": "Product 2",
	"price": "22.22",
	"quantity_in_stock": 20
  }'
```

### Get the Products List `GET /products/`
```bash
curl --request GET \
  --url http://localhost:8000/products/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```

### Add a Product to Order `POST /products/{product_id}/add_to_order/`
```bash
curl --request POST \
  --url http://localhost:8000/products/1/add_to_order/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```
This will add a quantity of 1 Product to a current Order that you have active (only one at a time). If there is no active order, one will be created.

### Remove Product from Order `POST /products/{product_id}/remove_from_order/`
```bash
curl --request POST \
  --url http://localhost:8000/products/1/remove_from_order/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```
This will remove the Product {product_id} from the Order in a quantity of 1.

### Submit my Order `POST /orders/{order_id}/submit/`
This will submit the current active Order with the products on it, and make the proper Stock changes in the products themselves. I only update the stock once I submit the order, but if there is no stock it won't let you add the product on the previous step anyway. So stock is checked both when adding the Product to the Order, and when submitting, but changes to the Product Stock are only made persistent once we Submit the Order.
```bash
curl --request POST \
  --url http://localhost:8000/orders/4/submit/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```
### Get all my Orders `GET /orders/`
```bash
curl --request GET \
  --url http://localhost:8000/orders/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```
### Get Current Active Order `GET /orders/current/`
```bash
curl --request GET \
  --url http://localhost:8000/orders/current/ \
  --header 'Authorization: Token 033e4e9652c885c961fc1143eac575794c1b76c8'
```

# Deployment Notes
As you can see the App is packaged into a Docker container. Some changes I would need to do to make it deployable in production:
- Add env Variables to be fed through the docker env into the settings. These could be anything that is external to the application such as DB host, password, username, db_name, environment (prod, dev, test, stage, etc).
- These variables could come from a `prod.env` or be fed into the container through a bash script gathering output from a IAC tool such as Terraform.
- I would then have a pipeline (Github Actions, Gitlab Pipelines, etc) that can check for things like:
  - PyLint
  - PEP8 (Flake8)
  - isort (imports)
  - black (formatting)
  - mypy (static type checking if needed)
  - Test execution
- Once all the checks are done, I would:
  - If trigger is `main`/`master` branch:
    - Build a new image with the commit snapshot of the code and push it to the image repository.
    - Trigger any Orchestration software to update the service with the new tag created for Prod environment.
  - If trigger is any other branch:
    - Same as above, but just trigger Orchestration software to update the Staging environment.

For all of this I would set up in AWS an RDS (can be set up by Terraform and given the proper outputs to feed the env variables of the containers) and a EKS cluster on top of an EC2 AutoScale group of instances.

I would also need a domain name from Route53 with a Public IP for outside access, and security Groups for the different services (Web, DB, Workers, Redis etc) to have connectivity with each other.

With this we can nicely Scale through EC2 Resources given a threshold of usage, and EKS can take advantage of these resources to scale up and down any services that require it. We can leverage Kubernetes to apply any Deployment strategy that we want to ensure no downtime (Blue/Green, Canary Deployment, etc.)