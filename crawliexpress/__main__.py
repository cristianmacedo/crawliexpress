import click

from lib import helpers
from lib import crawler

@click.group()
@click.option('-r', '--region', default='US', help='Region code [CC]')
@click.option('-c', '--country', default='usa', help='Country code [ccc]')
@click.option('-l', '--locale', default='en_US', help='Language/Country code [lc_CC]')
@click.option('-cr', '--currency', default='USD', help='Currency code [CCC]')
def cli(region, country, locale, currency):
  global crawliexpress
  crawliexpress = crawler.AliexpressCrawler(region=region, country=country, locale=locale, currency=currency)
  pass
        
@click.command()
@click.option('-p', '--product-id', required=True, type=str, help='Target product id')
def product(product_id):
  crawliexpress_product_result = crawliexpress.product(product_id)
  print(crawliexpress_product_result)

@click.command()
@click.option('-p', '--product-id', required=True, type=str, help='Target product id')
@click.option('-o', '--only-from-my-country', default=False, help='Only reviews from the selected contry')
@click.option('-m', '--max-pages', default=40, help='Maximum ammount of review pages')
@click.option('-t/-nt', '--translate/--no-translate', default=True, help='Translate to selected language')
def reviews(product_id, translate, only_from_my_country, max_pages):
  crawliexpress_reviews_results = crawliexpress.reviews(product_id=product_id, translate=translate, only_from_my_country=only_from_my_country, max_pages=max_pages)
  helpers.save_file(crawliexpress_reviews_results, f'dist/crawliexpress-reviews-{product_id}', 'csv')

cli.add_command(product)
cli.add_command(reviews)

# crawliexpress_categories_results = crawliexpress.categories()
# print(crawliexpress_categories_results[:10])
# helpers.save_file(crawliexpress_categories_results, f'../database/products', 'json')

if __name__ == '__main__':
  cli()