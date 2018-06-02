from client.publicRequests import PublicRequests


def main(product, collection, length):
    pr = PublicRequests(product = product)
    pr.get_last_missing_rates(collection, granularity=length)


if __name__ == '__main__':
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Complete a collection by adding the last missing candles.",
        epilog=textwrap.dedent('''

            example :
            python complete_database.py BTC-EUR btc_eur_candles_900 900
            ___
            '''))
    
    parser.add_argument("product", help="product of the collection (ex: BTC-EUR)", type=str)
    parser.add_argument("collection", help="collection to work on in the database", type=str)
    parser.add_argument("length", help="length of the candles of the given collection", type=int)

    args = parser.parse_args()

    main(args.product,args.collection, args.length)