# Python CCY Exchange Rate Task

For this task we want you to scrape live currency exchange rate data from
https://uk.finance.yahoo.com/currencies/

You will write a server that will receive and answer queries coming from
any number of clients. This is similar to something you might work on
while at Mollybet.

## Getting started

You should make a python3.8 virtual env, and then install the dependencies in
requirements.txt

```bash
python3 -m venv env
. ./env/bin/activate
pip install -r requirements.txt
```

Inside `yahoo_scraper/__main__.py` you'll find a simple server that listens on
localhost 8080. Make sure you've activated the env and then start it with:

```bash
python -m yahoo_scraper
```

In another terminal you can connect to it as a client with `nc localhost 8080`
and send some requests, this is how we will test your solution.

```bash
$ nc localhost 8080
Connected!
EUR:USD
0.0
USD:EUR
0.0
```

## Your task

Complete the task by filling out the server so that it will scrape the live
exchange rate for any requested currency pair and send it back to the client.
We're happy for you to use any relatively common python library that you think
would help. If you do add it to the `requirements.in` file and then run:

```bash
pip-compile requirements.in > requirements.txt
```

This task is intentionally open ended, so you are free to structure the code
however you want, and make changes to the server if you think it will help.
Here are some things that we'll have in mind when judging your solution.

* Requirements: Does it handle multiple clients gracefully
* Correctness: Does the server fetch the correct rate from the yahoo website
* Speed: How long does the client wait for a rate
* Style: Is your code idiomatic python

As said before, the task is deliberately open ended, so don't hesitate to make
a change to the server or add new parts if you think it would need it.

Once you've written your solution do a small write up of how it works and what
changes (if any) you would make before deploying this server to production.
After that please zip all the files and send it back to us.

## Write Up - David Stewart

This server uses beautifulSoup and requests for web scraping the yahoo finance
live currency website. Multiple concurrent clients are possible using threading,
part of Python's standard library.

I converted the server to a class structure as I believe it made the code tidier.

When running the __main__.py script, the server starts on localhost and port 8080
as defined at the top of the script.

* Once the server has started, the server listens for client connection requests
  with the `listen_for_clients` method.
  * When the server receives a request, it accepts the connection and prints to
  console the client address.
  * Then the server starts a new thread of the `handle_clients` method for that
  specific client, which allows separate threads for each client connection.
* The thread for this client is then in the `handle_clients` method and enters the
 `while True` loop:
  * If the client types `exit`, then the `while True` loop breaks and the server 
    gracefully closes the connection to that specific client.
  * Else, the server expects a currency pair split by a colon:
    * If the client request is not correctly formatted, then they are prompted
      to correct their formatting.
    * If the correct formatting is used, then the `get_rate` method is invoked.
      * The yahoo page is requested and then converted into a BeautifulSoup `soup`
      Object.
      * Then the single table on the yahoo finance page is found and split into rows.
      * Then each row is checked for the currency pair:
        * If the currency pair is found, then the value is sent to the client.
        * If the inverse of the currency pair is found, then the server calculates
          the inverse of the currency pair to 4 significant figures and sends it
          to the client.
    * If no currency pair is found for the currency pair, then a string is sent
      to the client saying `Currency pair not found`.
* This `while True` loop continues until the client types exit or uses a
KeyboardInterrupt.


## Ideas about steps before deploying into Production/Future work

* Use a testing suite/continuous integration to check server is functioning
  correctly after manual tests.
* Change all error messages to `Bad_request` rather than different strings.
* Split out web scraper into a separate class.
* Allow system arguments to define hostname and port, with defaults, upon class
  instantiation.
* Allow requests to run simultaneously using a multiprocessing library, such
  as `multiprocessing`.
* Update `invert_rate` method to use `decimal` module to avoid floating point
  calculation errors.
