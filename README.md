# Crawliexpress

Crawliexpress is a Python library command line application to retrieve data from Aliexpress listings.

## Installation

Clone this repo and install the dependecies located on 'requirements.txt'

```bash
pip install -r requirements.txt
```

## Usage

Navigate to the repository folder and run the file with python

```bash
python crawliexpress -l pt_BR reviews -p 4000592298467 # Reviews translated to Brazillian Portuguese for the product with the ID '4000592298467'
python crawliexpress product -p 4000592298467 # Listing info for the product with the ID '4000592298467'
python crawliexpress categories -t 10 # Top 10 best selling products crawling all categories
```

## API

Documentation for each specific command available

---

### `crawliexpress [OPTIONS] COMMAND [OPTIONS]`

```bash
Options:
  -r, --region TEXT     Region code [CC]
  -c, --country TEXT    Country code [ccc]
  -l, --locale TEXT     Language/Country code [lc_CC]
  -cr, --currency TEXT  Currency code [CCC]
  --help                Show this message and exit.

Commands:
  categories  Best-selling products from all categories
  product     Listing info of a specific product
  reviews     Reviews of a specific product
```

---

### `categories [OPTIONS]`

Crawls the first page of all Aliexpress categories and returns an Object List `[{}]` with `-t` length with the best selling products.

```bash
Options:
  -t, --top INTEGER  Top listing size
  --help             Show this message and exit.
```

---

### `product [OPTIONS]`

Crawls the `-p` product page and returns object with listing info.

```bash
Options:
  -p, --product-id TEXT  Target product id  [required]
  --help                 Show this message and exit.
```

---

### `reviews [OPTIONS]`

Crawls the `-p` product page and returns an Object List `[{}]` with custommer reviews.

```bash
Options:
  -p, --product-id TEXT                 Target product id  [required]
  -o, --only-from-my-country TEXT       Only reviews from the selected contry
  -m, --max-pages INTEGER               Maximum ammount of review pages
  -t, --translate / -nt, --no-translate Translate to selected language
  --help                                Show this message and exit.
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](./LICENSE)
