import click
import json

from lib import helpers
from lib import crawler

@click.group()
@click.option('-r', '--region', default='US', help='Region code [CC]')
@click.option('-c', '--country', default='usa', help='Country code [ccc]')
@click.option('-l', '--locale', default='en_US', help='Language/Country code [lc_CC]')
@click.option('-cr', '--currency', default='USD', help='Currency code [CCC]')
@click.pass_context
def cli(ctx, region, country, locale, currency):
  ctx.ensure_object(dict)
  ctx.obj['crawliexpress'] = crawler.AliexpressCrawler(region=region, country=country, locale=locale, currency=currency)
        
@click.command(help='Listing info of a specific product')
@click.option('-p', '--product-id', required=True, type=str, help='Target product id')
@click.pass_context
def product(ctx, product_id):
  crawliexpress_product_result = ctx.obj['crawliexpress'].product(product_id)
  if(crawliexpress_product_result): click.echo(json.dumps(crawliexpress_product_result, indent=2))

@click.command(help='Reviews of a specific product')
@click.option('-p', '--product-id', required=True, type=str, help='Target product id')
@click.option('-o', '--only-from-my-country', default=False, help='Only reviews from the selected contry')
@click.option('-m', '--max-pages', default=40, help='Maximum ammount of review pages')
@click.option('-t/-nt', '--translate/--no-translate', default=True, help='Translate to selected language')
@click.pass_context
def reviews(ctx, product_id, translate, only_from_my_country, max_pages):
  crawliexpress_reviews_results = ctx.obj['crawliexpress'].reviews(product_id=product_id, translate=translate, only_from_my_country=only_from_my_country, max_pages=max_pages)
  if(crawliexpress_reviews_results): helpers.save_file(crawliexpress_reviews_results, f'dist/crawliexpress-reviews-{product_id}', 'csv')

@click.command(help='Best-selling products from all categories')
@click.option('-t', '--top', default=10, help='Top listing size')
@click.pass_context
def categories(ctx, top):
  crawliexpress_categories_results =  ctx.obj['crawliexpress'].categories()
  if(crawliexpress_categories_results):
    click.echo(crawliexpress_categories_results[:top])
    helpers.save_file(crawliexpress_categories_results, f'../database/products', 'json')

cli.add_command(product)
cli.add_command(reviews)
cli.add_command(categories)

if __name__ == '__main__':
  cli()